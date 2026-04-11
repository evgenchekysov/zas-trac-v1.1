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
from core.errors import NotFound, Forbidden, InvalidTransition
from core.ticket import TicketStatus


class TicketService:
    def __init__(
        self,
        ticket_repo,
        session_repo,
        audit_service,
        session_service,
    ):
        self.ticket_repo = ticket_repo
        self.session_repo = session_repo
        self.audit = audit_service
        self.session_service = session_service

    # -------------------------------------------------
    # STATUS AGGREGATION
    # -------------------------------------------------

    async def recalc_status(self, ticket_id: UUID):
        """
        Агрегирует статус заявки на основе сессий.
        Вызывается после start/stop session.
        """

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        
# DONE и CLOSED — финальные, не агрегируем
    if ticket.status in {TicketStatus.DONE, TicketStatus.CLOSED}:
        return ticket.status

    # ✅ ЗАЩИТА NEW / ASSIGNED (рекомендуемый вариант)
    if ticket.status in {TicketStatus.NEW, TicketStatus.ASSIGNED}:
        return ticket.status


        active_sessions = await self.session_repo.count_active_sessions(
            ticket_id
        )

        new_status = (
            TicketStatus.IN_PROGRESS
            if active_sessions > 0
            else TicketStatus.PAUSED
        )

        if new_status != ticket.status:
            await self.ticket_repo.update_status(ticket_id, new_status)

            await self.audit.log_event(
                type="ticket_status_aggregated",
                payload={
                    "ticket_id": str(ticket_id),
                    "status": new_status.value,
                },
            )

        return new_status

    # -------------------------------------------------
    # MARK DONE
    # -------------------------------------------------

    async def mark_done(self, ticket_id: UUID, user_id: UUID):
        """
        Завершение работ по заявке.
        Может быть выполнено ЛЮБЫМ participant.
        """

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        if ticket.status in {TicketStatus.DONE, TicketStatus.CLOSED}:
            raise InvalidTransition("ticket already finished")

        if not await self.ticket_repo.is_participant(ticket_id, user_id):
            raise Forbidden("user is not participant")

        # 1. Переводим заявку в DONE
        await self.ticket_repo.update_status(ticket_id, TicketStatus.DONE)

        await self.audit.log_event(
            type="ticket_marked_done",
            payload={
                "ticket_id": str(ticket_id),
                "user_id": str(user_id),
            },
        )

        # 2. Завершаем ВСЕ активные сессии
        await self.session_service.handle_ticket_done(ticket_id)

        return TicketStatus.DONE

    # -------------------------------------------------
    # CLOSE TICKET
    # -------------------------------------------------

    async def close_ticket(self, ticket_id: UUID, user_id: UUID, is_admin: bool):
        """
        Финальное закрытие заявки.
        Допустимо только из DONE.
        """

        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise NotFound("ticket not found")

        if ticket.status != TicketStatus.DONE:
            raise InvalidTransition("ticket must be DONE before closing")

        if not (is_admin or ticket.owner_id == user_id):
            raise Forbidden("only owner or admin can close ticket")

        await self.ticket_repo.update_status(ticket_id, TicketStatus.CLOSED)

        await self.audit.log_event(
            type="ticket_closed",
            payload={
                "ticket_id": str(ticket_id),
                "user_id": str(user_id),
            },
        )

        return TicketStatus.CLOSED
