from uuid import UUID


class SystemService:
    def __init__(self, session_repo, ticket_repo, audit_service):
        self.session_repo = session_repo
        self.ticket_repo = ticket_repo
        self.audit = audit_service

    async def close_shift(self):
        """
        Закрытие смены (например, 23:00).
        1. Останавливает ВСЕ активные сессии
        2. Переводит тикеты в PAUSED, если никто не работает
        """

        # 1. Получаем все активные сессии
        sessions = await self.session_repo.get_all_active_sessions()

        affected_tickets = set()

        # 2. Закрываем сессии
        for session in sessions:
            await self.session_repo.stop_session(
                session_id=session["id"],
                reason="shift_ended",
            )

            await self.audit.log_event(
                event_type="session_stopped_due_shift_end",
                user_id=str(session["user_id"]),
                ticket_id=str(session["ticket_id"]),
                payload={
                    "session_id": str(session["id"])
                    
                }
            )

            affected_tickets.add(session["ticket_id"])

        # 3. Обновляем статусы тикетов
        for ticket_id in affected_tickets:

            active = await self.session_repo.count_active_sessions(ticket_id)

            if active == 0:
                ticket = await self.ticket_repo.get(ticket_id)

                # ✅ только деградация статуса
                if ticket["status"] == "IN_PROGRESS":
                    await self.ticket_repo.update_status(
                        ticket_id,
                        "PAUSED",
                    )

                    
            await self.audit.log_event(
                event_type="ticket_paused_due_shift_end",
                user_id="system",
                ticket_id=str(ticket_id),
                payload={
                    "reason": "shift_end"
                }
            )

