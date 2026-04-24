class Ticket_Workflow:
    def __init__(self, ticket_service):
        self.ticket_service = ticket_service

    async def create_ticket(self, creator_id):
        return await self.ticket_service.create_ticket(
            creator_id=creator_id
        )

    async def join_ticket(self, ticket_id, user_id):
        await self.ticket_service.join_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    async def leave_ticket(self, ticket_id, user_id):
        await self.ticket_service.leave_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    async def mark_done(self, ticket_id, user_id):
        await self.ticket_service.mark_done(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    async def close_ticket(self, ticket_id, user_id):
        await self.ticket_service.close_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
        )

    async def list_tickets(self):
        return await self.ticket_service.list_tickets()

    async def get_ticket(self, ticket_id):
        return await self.ticket_service.get_ticket(ticket_id)
