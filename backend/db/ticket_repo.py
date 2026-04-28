from multiprocessing import pool
from uuid import UUID
from domain.ticket import TicketStatus
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
                insert into tickets (created_by, status)
                values ($1, $2)
                returning *
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


    async def update_status(self, ticket_id: int, status):
        raise NotImplementedError

    async def is_participant(self, ticket_id: int, user_id: UUID) -> bool:
        raise NotImplementedError
    