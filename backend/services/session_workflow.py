class Session_Workflow:
    def __init__(self, session_service, ticket_service):
        self.session_service = session_service
        self.ticket_service = ticket_service

    async def start_session(self, user_id, ticket_id):
        session = await self.session_service.start_session(user_id, ticket_id)
        await self.ticket_service.recalc_status(ticket_id)
        return session

    async def stop_session(self, user_id):
        active = await self.session_service.stop_active_session(user_id)
        if active:
            await self.ticket_service.recalc_status(active.ticket_id)
        return active
