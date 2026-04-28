from uuid import UUID
from typing import List, Optional
from db.pool import get_pool

class SessionRepo:

    async def start_session(self, ticket_id: int, user_id: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO work_sessions (ticket_id, user_id, started_at)
                VALUES ($1, $2, now())
                RETURNING *
                """,
                ticket_id,
                user_id,
            )

    async def get_active_session(self, user_id: str):
        """
        Возвращает активную сессию пользователя или None.
        """
        
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT *
                FROM work_sessions
                WHERE user_id = $1 AND stopped_at IS NULL
                """,
                user_id,
            )


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
