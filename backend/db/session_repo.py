from uuid import UUID
from typing import List, Optional


class SessionRepo:
    async def get_active_session(self, user_id: UUID):
        """
        Возвращает активную сессию пользователя или None.
        """
        raise NotImplementedError

    async def create_session(self, ticket_id: UUID, user_id: UUID):
        """
        Создаёт новую рабочую сессию.
        """
        raise NotImplementedError

    async def stop_session(self, session_id: UUID, reason: str):
        """
        Завершает сессию с указанием причины.
        """
        raise NotImplementedError

    async def get_active_sessions_by_ticket(self, ticket_id: UUID) -> List:
        """
        Возвращает все активные сессии по заявке.
        """
        raise NotImplementedError
