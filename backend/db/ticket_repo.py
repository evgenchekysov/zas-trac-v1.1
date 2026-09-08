from uuid import UUID

from domain.ticket import (
    TicketStatus,
    TicketPriority,
)

from db.pool import get_pool


class TicketRepo:
    def __init__(self):
        self._pool = None

    async def _get_conn(self):
        if self._pool is None:
            self._pool = await get_pool()
        return self._pool

    async def create_ticket(self, creator_id, status: TicketStatus):
        pool = await self._get_conn()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO tickets (created_by, status)
                VALUES ($1, $2)
                RETURNING *
                """,
                creator_id,
                status.value,
            )

            return dict(row) if row else None

    async def get(self, ticket_id: int):
        pool = await self._get_conn()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT *
                FROM tickets
                WHERE id = $1
                """,
                ticket_id,
            )

        return dict(row) if row else None

    async def update_status(
        self,
        ticket_id: int,
        status,
    ):
        pool = await get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets
                SET status = $2,
                    updated_at = NOW()
                WHERE id = $1
                """,
                ticket_id,
                status,
            )

    async def update_priority(
        self,
        ticket_id: int,
        priority: TicketPriority,
    ):
        pool = await self._get_conn()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets
                SET priority = $2,
                    updated_at = NOW()
                WHERE id = $1
                """,
                ticket_id,
                priority.value,
            )

    async def lock_priority(
        self,
        ticket_id: int,
    ):
        pool = await self._get_conn()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets
                SET priority_state = 'LOCKED',
                    updated_at = NOW()
                WHERE id = $1
                """,
                ticket_id,
            )

    async def is_participant(
        self,
        ticket_id: int,
        user_id: str,
    ) -> bool:
        pool = await get_pool()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM participants
                WHERE ticket_id = $1
                AND user_id = $2
                """,
                ticket_id,
                user_id,
            )

            return row is not None

    async def get_all_tickets(self):
        pool = await self._get_conn()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    t.id,
                    t.status,
                    t.priority,
                    t.priority_state,
                    t.created_at,

                    EXISTS (
                        SELECT 1
                        FROM work_sessions ws
                        WHERE ws.ticket_id = t.id
                        AND ws.stopped_at IS NULL
                    ) AS is_active

                FROM tickets t
                ORDER BY t.created_at DESC
                """
            )

            return [dict(row) for row in rows]
