from typing import List
from db.pool import get_pool


class ParticipantRepo:
    async def add(self, ticket_id: int, user_id: str):
        """
        Добавляет участника в заявку.
        Идемпотентно (повторный join не ломается).
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO participants (ticket_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                ticket_id,
                user_id,
            )

    async def remove(self, ticket_id: int, user_id: str):
        """
        Удаляет участника из заявки.
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM participants
                WHERE ticket_id = $1 AND user_id = $2
                """,
                ticket_id,
                user_id,
            )

    async def list_by_ticket(self, ticket_id: int) -> List[str]:
        """
        Возвращает список пользователей-участников заявки.
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT user_id
                FROM participants
                WHERE ticket_id = $1
                """,
                ticket_id,
            )
            return [str(row["user_id"]) for row in rows]
        
    
    async def is_participant(self, ticket_id: int, user_id: str) -> bool:
        """
        Проверяет, является ли пользователь участником заявки.
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM participants
                WHERE ticket_id = $1 AND user_id = $2
                """,
                ticket_id,
                user_id,
            )
            return row is not None
