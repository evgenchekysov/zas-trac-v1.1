"""
Ticket CRUD operations.

Day 29:
- function signatures only
- no SQL yet
"""

from typing import Any


async def create_ticket(pool, data: dict) -> Any:
    raise NotImplementedError


async def get_ticket_by_id(pool, ticket_id: str) -> Any:
    raise NotImplementedError


async def list_tickets(pool) -> list[Any]:
    raise NotImplementedError


async def update_ticket_status(pool, ticket_id: str, status: str) -> None:
    raise NotImplementedError
