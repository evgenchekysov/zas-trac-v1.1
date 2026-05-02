"""
ZAS-TRAC — Ticket Service
========================

ДАННЫЙ ФАЙЛ ЯВЛЯЕТСЯ АРХИТЕКТУРНЫМ КОНТРАКТОМ.

В нём зафиксированы бизнес-правила работы с заявками и рабочим временем.
Любая реализация логики в backend ОБЯЗАНА строго соответствовать
описанным ниже правилам.

-------------------------------------------------
ОБЩИЕ ПРИНЦИПЫ
-------------------------------------------------

1. Идентификация пользователей
- user_id всегда определяется через Supabase Auth (auth.uid).
- user_id никогда не принимается из frontend или Telegram.

2. Роли и доступ
- Backend не реализует RBAC.
- Backend не хранит роли пользователей.
- Контроль доступа осуществляется на уровне Supabase RLS.
- Backend отвечает только за бизнес-правила и их соблюдение.

3. Разделение ответственности
- Ticket Service определяет допустимые действия.
- Session Service учитывает личное рабочее время.
- CRUD слой не содержит бизнес-логики.
--------------------------------------------------------------------
ИНВАРИАНТ АРХИТЕКТУРЫ (ADR-00X)

created_by (creator) — исключительно историческая роль
(кто инициировал заявку).

owner — явная операционная ответственность
(кто отвечает за заявку в текущий момент).

ВАЖНО:
creator НИКОГДА не используется как fallback для owner
ни при каких обстоятельствах, включая:
- смену статусов заявки;
- автоматические и batch‑операции (в т.ч. D+30);
- нормализацию или восстановление данных.

Назначение или смена owner возможны
только через явные бизнес‑правила
или административные действия.

Данное правило зафиксировано архитектурно
и не подлежит изменению без отдельного решения.
--------------------------------------------------------------------

-------------------------------------------------
СТАТУСНАЯ МОДЕЛЬ ЗАЯВКИ
-------------------------------------------------

Допустимые статусы:

NEW          — заявка создана, работа не начата
ASSIGNED     — исполнитель назначен администратором (опционально)
IN_PROGRESS  — по заявке есть хотя бы одна активная сессия
PAUSED       — по заявке нет активных сессий
DONE         — работы по заявке завершены
CLOSED       — заявка официально закрыта и архивирована


-------------------------------------------------
ДОПУСТИМЫЕ ПЕРЕХОДЫ
-------------------------------------------------

NEW → ASSIGNED
NEW → IN_PROGRESS
ASSIGNED → IN_PROGRESS

IN_PROGRESS → PAUSED
PAUSED → IN_PROGRESS

IN_PROGRESS → DONE
DONE → CLOSED


Недопустимо:
- пропуск статусов
- возврат из DONE или CLOSED
- прямое закрытие из IN_PROGRESS


-------------------------------------------------
КЛЮЧЕВОЕ РАЗДЕЛЕНИЕ ПОНЯТИЙ
-------------------------------------------------

1. СЕССИЯ
- Сессия отражает ЛИЧНОЕ рабочее время конкретного пользователя.
- Сессия принадлежит одному user_id.
- Пользователь может управлять ТОЛЬКО своей сессией.

2. ЗАЯВКА
- Статус заявки отражает ОБЩЕЕ состояние работ.
- Статус заявки является агрегированным результатом
  наличия или отсутствия активных сессий.

Сессии — персональные.
Статус заявки — коллективный.


-------------------------------------------------
ПРАВИЛА РАБОТЫ С СЕССИЯМИ
-------------------------------------------------

1. Начать работу
- Пользователь должен быть participant заявки.
- Статус заявки должен быть IN_PROGRESS.
- У пользователя может быть только одна активная сессия в системе.

2. Автоматическая пауза при переключении между заявками
- Если у пользователя есть активная сессия по заявке A
  и он начинает работу по заявке B:
  * активная сессия по заявке A автоматически завершается
    с причиной "auto_paused"
  * другие участники заявки A не затрагиваются
  * статус заявки A принудительно не меняется

3. Остановить работу
- Пользователь останавливает ТОЛЬКО свою сессию.
- Остановка сессии одного участника
  не влияет на сессии других участников.

4. Переход заявки в PAUSED
- Заявка считается PAUSED,
  если и только если по ней отсутствуют активные сессии.
- Ни один participant не может поставить заявку
  на паузу "за всех".


-------------------------------------------------
ЗАВЕРШЕНИЕ РАБОТ (DONE)
-------------------------------------------------

IN_PROGRESS → DONE

Смысл:
- DONE означает завершение работ по заявке В ЦЕЛОМ.
- DONE не является индивидуальным действием.

Кто может установить DONE:
- любой participant заявки,
  фактически завершивший последние работы.

При переходе в DONE:
- статус заявки переводится в DONE
- все АКТИВНЫЕ сессии по заявке
  автоматически завершаются
  с причиной "status_done"
- запуск новых сессий запрещён


-------------------------------------------------
ЗАКРЫТИЕ ЗАЯВКИ (CLOSED)
-------------------------------------------------

DONE → CLOSED

Смысл:
- CLOSED — финальный и необратимый статус.
- Заявка закрыта, проверена и архивирована.
- Дальнейшие действия по заявке запрещены.

Кто может закрыть:
- owner заявки
- admin


-------------------------------------------------
UI-КОНТРАКТ (КНОПКИ)
-------------------------------------------------

1. ▶ Начать работу
- запускает личную сессию пользователя

2. ⏸ Остановить работу
- завершает личную сессию пользователя

3. ✅ Работы выполнены
- переводит заявку из IN_PROGRESS в DONE

4. 🔒 Закрыть заявку
- переводит заявку из DONE в CLOSED

Других кнопок и состояний не предусмотрено.
Отсутствуют:
- кнопка «Поставить заявку на паузу»
- кнопка «Закончить свою работу» как отдельное действие


-------------------------------------------------
КОНЕЦ АРХИТЕКТУРНОГО КОНТРАКТА
-------------------------------------------------
"""
from uuid import UUID
from domain import ticket
from core.errors import NotFound, Forbidden, InvalidStatusTransition
from domain.ticket import TicketStatus



class TicketService:
    def __init__(
        self,
        ticket_repo,
        session_repo,
        participant_repo,
        audit_service,
        session_service,
    ):
        self.ticket_repo = ticket_repo
        self.session_repo = session_repo
        self.participant_repo = participant_repo
        self.audit = audit_service
        self.session_service = session_service

    # -------------------------------------------------
    # CREATE TICKET
    # -------------------------------------------------

    async def create_ticket(self, creator_id):
        
        """
        Создание новой заявки.
        Статус: NEW
        """

        ticket = await self.ticket_repo.create_ticket(
            creator_id=creator_id,
            status=TicketStatus.NEW,
        )

        await self.audit.log_event(
            event_type="ticket_created",
            user_id=str(creator_id),
            ticket_id=str(ticket["id"]),
        )

        return ticket


    # -------------------------------------------------
    # JOIN TICKET
    # -------------------------------------------------
    async def join_ticket(self, ticket_id: int, user_id: str):
        """
        Присоединение пользователя к заявке как participant.
        Не меняет статус заявки.
        """

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        # статус из БД приходит строкой
        status = TicketStatus(ticket["status"])

        # ✅ Запрещено присоединение к завершённым тикетам
        if status == TicketStatus.DONE:
            raise Forbidden("cannot join finished ticket")

        # ✅ Добавление участника (идемпотентно — контроль в БД)
        await self.participant_repo.add(
            ticket_id=ticket_id,
            user_id=user_id,
        )

        await self.audit.log_event(
            event_type="ticket_joined",
            user_id=str(user_id),
            ticket_id=str(ticket_id),
        )


    # -------------------------------------------------
    # LEAVE TICKET
    # -------------------------------------------------
    async def leave_ticket(self, ticket_id: int, user_id: str):
        """
        Выход пользователя из заявки (participant).
        Не меняет статус заявки.
        """

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        status = TicketStatus(ticket["status"])

        # ✅ Не выходим из завершённых тикетов
        if status == TicketStatus.DONE:
            raise Forbidden("cannot leave finished ticket")

        # ✅ Удаление участника (идемпотентно)
        await self.participant_repo.remove(
            ticket_id=ticket_id,
            user_id=user_id,
        )

        await self.audit.log_event(
            event_type="ticket_left",
            user_id=str(user_id),
            ticket_id=str(ticket_id),
        )

    # -------------------------------------------------
    # MARK DONE
    # -------------------------------------------------
    async def mark_done(self, ticket_id: UUID, user_id: UUID):

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        status = TicketStatus(ticket["status"])

        if status in {TicketStatus.DONE, TicketStatus.CLOSED}:
            raise InvalidStatusTransition("ticket already finished")

        if not await self.ticket_repo.is_participant(ticket_id, user_id):
            raise Forbidden("user is not participant")

        # ✅ НОВОЕ ПРАВИЛО
        active = await self.session_repo.count_active_sessions(ticket_id)

        if active == 0:
            raise Forbidden("cannot mark DONE without active work session")

        # ✅ DONE
        await self.ticket_repo.update_status(
            ticket_id,
            TicketStatus.DONE.value,
        )

        await self.audit.log_event(
            event_type="ticket_marked_done",
            user_id=str(user_id),
            ticket_id=str(ticket_id),
            payload={},
        )

        # ✅ закрываем сессии
        await self.session_service.handle_ticket_done(ticket_id)

        return TicketStatus.DONE

    # -------------------------------------------------
    # CLOSE TICKET
    # -------------------------------------------------

    async def close_ticket(self, ticket_id: UUID, user_id: UUID, is_admin: bool):

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        status = TicketStatus(ticket["status"])   # ✅

        if status != TicketStatus.DONE:
            raise InvalidStatusTransition("ticket must be DONE before closing")

        # ❗ тут внимательно — ticket.owner_id у тебя может быть dict
        if not (is_admin or ticket["owner_id"] == user_id):
            raise Forbidden("only owner or admin can close ticket")

        await self.ticket_repo.update_status(
            ticket_id,
            TicketStatus.CLOSED.value,   # ✅ .value
        )

        await self.audit.log_event(
            event_type="ticket_closed",
            user_id=str(user_id),
            ticket_id=str(ticket_id),
            payload={},
        )

        return TicketStatus.CLOSED
    
    # -------------------------------------------------
    # START SESSION
    # -------------------------------------------------
    async def start_session(self, ticket_id: int, user_id: str):

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        status = TicketStatus(ticket["status"])
        if status == TicketStatus.DONE:
            raise Forbidden("cannot start session on finished ticket")

        # ✅ Пользователь должен быть участником
        if not await self.participant_repo.is_participant(ticket_id, user_id):
            raise Forbidden("user is not participant")

        # ✅ ВОТ ЭТО ГЛАВНОЕ — создаём session
        session = await self.session_service.start_session(user_id, ticket_id)

        # ✅ статус обновляем ПОСЛЕ
        if ticket["status"] != "IN_PROGRESS":
            await self.ticket_repo.update_status(
                ticket_id,
                TicketStatus.IN_PROGRESS.value,
            )

        return session

    # -------------------------------------------------
    # AUTO PAUSE (CONTROLLED)
    # -------------------------------------------------

    async def maybe_pause_ticket(self, ticket_id: int):

        ticket = await self.ticket_repo.get(ticket_id)

        if ticket["status"] != "IN_PROGRESS":
            return

        active = await self.session_repo.count_active_sessions(ticket_id)

        if active == 0:
            await self.ticket_repo.update_status(
                ticket_id,
                TicketStatus.PAUSED.value,
            )


        await self.audit.log_event(
            event_type="ticket_auto_paused",
            user_id="system",               # ✅ системное событие
            ticket_id=str(ticket_id),
            payload={}
        )
    # -------------------------------------------------
    # LIST TICKETS (READ)
    # -------------------------------------------------
    async def list_tickets(self):
        return await self.ticket_repo.get_all_tickets()
        
    
    # -------------------------------------------------
    # GET TICKET (READ)
    # -------------------------------------------------
    async def get_ticket(self, ticket_id: int):
        ticket = await self.ticket_repo.get(ticket_id)

        if not ticket:
            raise NotFound("ticket not found")

        return ticket
