from core.errors import (
    NotFound,
    InvalidStatusTransition,
)

from domain.ticket import (
    TicketStatus,
    TicketPriority,
)


class Ticket_Workflow:
    def __init__(self, ticket_service):
        self.ticket_service = ticket_service

    # -------------------------------------------------
    # CREATE TICKET
    # -------------------------------------------------

    async def create_ticket(self, creator_id):
        return await self.ticket_service.create_ticket(
            creator_id=creator_id
        )

    # -------------------------------------------------
    # JOIN TICKET
    # -------------------------------------------------

    async def join_ticket(self, ticket_id, user_id):
        await self.ticket_service.join_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    # -------------------------------------------------
    # LEAVE TICKET
    # -------------------------------------------------

    async def leave_ticket(self, ticket_id, user_id):
        await self.ticket_service.leave_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    # -------------------------------------------------
    # MARK DONE
    # -------------------------------------------------

    async def mark_done(self, ticket_id, user_id):
        await self.ticket_service.mark_done(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    # -------------------------------------------------
    # CLOSE TICKET
    # -------------------------------------------------

    async def close_ticket(
        self,
        ticket_id,
        user_id,
        is_admin: bool,
    ):
        await self.ticket_service.close_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
            is_admin=is_admin,
        )

    # -------------------------------------------------
    # LIST TICKETS
    # -------------------------------------------------

    async def list_tickets(self):
        return await self.ticket_service.list_tickets()

    # -------------------------------------------------
    # GET TICKET
    # -------------------------------------------------

    async def get_ticket(self, ticket_id):
        return await self.ticket_service.get_ticket(ticket_id)

    # -------------------------------------------------
    # START SESSION
    # -------------------------------------------------

    async def start_session(
        self,
        ticket_id,
        user_id,
    ):
        ticket = await self.ticket_service.get_ticket(ticket_id)

        if not ticket:
            raise NotFound("ticket not found")

        status = TicketStatus(ticket["status"])

        # ADR‑003 / WTS lifecycle
        if status not in {
            TicketStatus.NEW,
            TicketStatus.ASSIGNED,
            TicketStatus.PAUSED,
        }:
            raise InvalidStatusTransition(
                "cannot start"
            )

        # создаём фактическую рабочую сессию
        await self.ticket_service.start_session(
            ticket_id=ticket_id,
            user_id=user_id,
        )

        # статус меняется только через Workflow
        if status != TicketStatus.IN_PROGRESS:
            await self.ticket_service.ticket_repo.update_status(
                ticket_id,
                TicketStatus.IN_PROGRESS.value,
            )

    # -------------------------------------------------
    # STOP SESSION
    # -------------------------------------------------

    async def stop_session(
        self,
        ticket_id,
        user_id,
    ):
        await self.ticket_service.stop_session(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    # -------------------------------------------------
    # PRIORITY
    # ADR‑008 Foundation
    # -------------------------------------------------

    async def change_priority(
        self,
        ticket_id,
        priority: TicketPriority,
        user_id,
    ):
        """
        Изменение Priority.

        Пока:
        - без Review Flow
        - без Dispatcher Approval
        - только базовый ADR‑008
        """

        return await self.ticket_service.change_priority(
            ticket_id=ticket_id,
            priority=priority,
            user_id=user_id,
        )

    async def lock_priority(
        self,
        ticket_id,
        user_id,
    ):
        """
        Фиксация Priority.

        После LOCKED изменение запрещено.
        """

        return await self.ticket_service.lock_priority(
            ticket_id=ticket_id,
            user_id=user_id,
        )
