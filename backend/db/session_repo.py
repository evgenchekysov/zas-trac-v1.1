from typing import List
from db.pool import get_pool


class SessionRepo:

    # ✅ CREATE SESSION
    
    async def create_session(self, ticket_id: int, user_id: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():   # ✅ ВОТ ЭТО КЛЮЧ
                session = await conn.fetchrow(
                    """
                    INSERT INTO work_sessions (ticket_id, user_id, started_at)
                    VALUES ($1, $2, NOW())
                    RETURNING *
                    """,
                    ticket_id,
                    user_id,
                )
                                
                print(">>> CREATE SESSION CALLED")
                print(">>> INSERT OK:", session)

                return session


    # ✅ GET ACTIVE SESSION (1 для пользователя)
    async def get_active_session(self, user_id: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT *
                FROM work_sessions
                WHERE user_id = $1
                  AND stopped_at IS NULL
                """,
                user_id,
            )

    # ✅ STOP SESSION (идемпотентный)
    async def stop_session(self, session_id: int, reason: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE work_sessions
                SET stopped_at = NOW(),
                    stop_reason = $2
                WHERE id = $1
                  AND stopped_at IS NULL
                """,
                session_id,
                reason,
            )

    # ✅ ВСЕ АКТИВНЫЕ СЕССИИ ПО ТИКЕТУ
    async def get_active_sessions_by_ticket(self, ticket_id: int) -> List:
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT *
                FROM work_sessions
                WHERE ticket_id = $1
                  AND stopped_at IS NULL
                """,
                ticket_id,
            )

    # ✅ ВСЕ АКТИВНЫЕ СЕССИИ
    async def get_all_active_sessions(self):
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT *
                FROM work_sessions
                WHERE stopped_at IS NULL
                """
            )

    # ✅ СКОЛЬКО АКТИВНЫХ ПО ТИКЕТУ
    async def count_active_sessions(self, ticket_id: int):
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM work_sessions
                WHERE ticket_id = $1
                  AND stopped_at IS NULL
                """,
                ticket_id,
            )