"""
ZAS-TRAC — Session Service
=========================

ДАННЫЙ ФАЙЛ ЯВЛЯЕТСЯ АРХИТЕКТУРНЫМ КОНТРАКТОМ
ДЛЯ УЧЁТА РАБОЧЕГО ВРЕМЕНИ (WORK SESSIONS).

Файл фиксирует бизнес-смысл сессий и правила их жизненного цикла.
Реализация логики должна строго соответствовать описанным ниже правилам
и согласовываться с Ticket Service.
Session Service отвечает ТОЛЬКО за учёт рабочего времени.
Не управляет статусами заявок и не принимает решений о них.
-------------------------------------------------
ОБЩИЕ ПРИНЦИПЫ
-------------------------------------------------

1. Назначение сессии
- Session отражает ФАКТИЧЕСКОЕ рабочее время конкретного пользователя.
- Session не существует сама по себе, всегда привязана к заявке (ticket_id).

2. Персональность
- Сессия всегда персональная.
- Сессия принадлежит ровно одному user_id.
- Пользователь может управлять ТОЛЬКО своей сессией.

3. Ограничение активности
- Пользователь может иметь НЕ БОЛЕЕ ОДНОЙ активной сессии
  в системе одновременно.
- Параллельные сессии запрещены.

4. Разделение ответственности
- Session Service отвечает за правила учёта времени.
- Ticket Service отвечает за статусы заявки.
- CRUD слой только читает и пишет данные, без логики.


-------------------------------------------------
УСЛОВИЯ НАЧАЛА СЕССИИ
-------------------------------------------------

Начать рабочую сессию можно ТОЛЬКО если одновременно выполняются условия:

1. Пользователь является participant заявки.
- Участник — пользователь, официально задействованный в работах
  (owner, назначенный или присоединившийся).

2. Статус заявки = IN_PROGRESS.
- В статусах NEW, ASSIGNED, PAUSED, DONE, CLOSED
  начало сессии запрещено.

3. У пользователя нет активной сессии
ИЛИ активная сессия будет автоматически поставлена на паузу
(см. ниже).


-------------------------------------------------
АВТОМАТИЧЕСКАЯ ПАУЗА ПРИ ПЕРЕКЛЮЧЕНИИ
-------------------------------------------------

Если пользователь пытается начать работу по заявке B,
при наличии активной сессии по заявке A:

- активная сессия по заявке A автоматически завершается
  с причиной "auto_paused"
- фиксируется фактически отработанное время
- сессии других участников заявки A не затрагиваются
- статус заявки A принудительно не меняется

Таким образом:
- пользователь всегда имеет только одну активную сессию
- временная помощь по другим заявкам учитывается корректно


-------------------------------------------------
ОСТАНОВКА СЕССИИ
-------------------------------------------------

Пользователь может в любой момент остановить свою сессию:

- при уходе домой
- при перерыве
- при передаче работ другому участнику

Правила:
- пользователь останавливает ТОЛЬКО свою сессию
- остановка сессии не влияет напрямую на статус заявки
- пользователь не может остановить чужие сессии

Остановленная сессия является завершённой
и не может быть возобновлена.


-------------------------------------------------
СВЯЗЬ С СТАТУСАМИ ЗАЯВКИ
-------------------------------------------------

- IN_PROGRESS → PAUSED
  Если по заявке отсутствуют активные сессии,
  она считается приостановленной.

- IN_PROGRESS → DONE
  При переходе заявки в DONE
  все АКТИВНЫЕ сессии по заявке автоматически завершаются
  с причиной "status_done".

- PAUSED → IN_PROGRESS
  Сессии не запускаются автоматически.
  Пользователь должен начать работу вручную.


-------------------------------------------------
ИНВАРИАНТЫ (ОБЯЗАТЕЛЬНЫ ДЛЯ РЕАЛИЗАЦИИ)
-------------------------------------------------

- Одна активная сессия на пользователя.
- Сессии всегда личные.
- Смена заявки останавливает ТОЛЬКО текущую сессию пользователя.
- DONE завершает только активные сессии, прошлые не изменяет.
- Учёт времени никогда не переписывается задним числом.


-------------------------------------------------
КОНЕЦ АРХИТЕКТУРНОГО КОНТРАКТА
-------------------------------------------------
"""

from uuid import UUID
from core.errors import NotFound, Forbidden


class SessionService:
    def __init__(self, session_repo, ticket_repo, audit_service):
        self.session_repo = session_repo
        self.ticket_repo = ticket_repo
        self.audit = audit_service

    # -------------------------------------------------
    # START SESSION
    # -------------------------------------------------

    async def start_session(self, user_id: UUID, ticket_id: UUID):
        """
        Начало рабочей сессии.
        Единственный публичный способ начать работу.
        """

        # 1. Проверяем, что заявка существует
        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        # 2. Проверяем participation
        if not await self.ticket_repo.is_participant(ticket_id, user_id):
            raise Forbidden("user is not participant of this ticket")

        # 3. Проверяем активную сессию пользователя
        active = await self.session_repo.get_active_session(user_id)

        # 4. Auto‑pause предыдущей сессии (если была)
        if active:
            await self.session_repo.stop_session(
                session_id=active.id,
                reason="auto_paused",
            )

            await self.audit.log_event(
                type="session_auto_paused",
                payload={
                    "session_id": str(active.id),
                    "ticket_id": str(active.ticket_id),
                    "user_id": str(user_id),
                },
            )

        # 5. Создаём новую сессию
        session = await self.session_repo.create_session(
            ticket_id=ticket_id,
            user_id=user_id,
        )

        # 6. Audit
        await self.audit.log_event(
            type="session_started",
            payload={
                "session_id": str(session.id),
                "ticket_id": str(ticket_id),
                "user_id": str(user_id),
            },
        )

        return session

    # -------------------------------------------------
    # STOP ACTIVE SESSION
    # -------------------------------------------------

    async def stop_active_session(self, user_id: UUID):
        """
        Останавливает ТОЛЬКО текущую активную сессию пользователя.
        Idempotent: если активной сессии нет — ничего не делает.
        """

        active = await self.session_repo.get_active_session(user_id)

        if not active:
            return None

        await self.session_repo.stop_session(
            session_id=active.id,
            reason="stopped_by_user",
        )

        await self.audit.log_event(
            type="session_stopped",
            payload={
                "session_id": str(active.id),
                "ticket_id": str(active.ticket_id),
                "user_id": str(user_id),
            },
        )

        return active

    # -------------------------------------------------
    # REACTIONS FROM TICKET SERVICE
    # -------------------------------------------------

    async def handle_ticket_done(self, ticket_id: UUID):
        """
        Реакция на перевод заявки в DONE.
        Вызывается ONLY из Ticket Service.
        """

        sessions = await self.session_repo.get_active_sessions_by_ticket(
            ticket_id
        )

        for session in sessions:
            await self.session_repo.stop_session(
                session_id=session.id,
                reason="status_done",
            )

            await self.audit.log_event(
                type="session_stopped_due_done",
                payload={
                    "session_id": str(session.id),
                    "ticket_id": str(ticket_id),
                    "user_id": str(session.user_id),
                },
            )
          
