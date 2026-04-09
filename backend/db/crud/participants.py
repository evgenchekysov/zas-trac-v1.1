"""
Ticket participants CRUD.

Day 29/early Day 30:
- signatures only
- no SQL
- no business logic
"""

from typing import Any, List


async def add_participant(pool, ticket_id: str, user_id: str) -> None:
    raise NotImplementedError


async def remove_participant(pool, ticket_id: str, user_id: str) -> None:
    raise NotImplementedError


async def is_participant(pool, ticket_id: str, user_id: str) -> bool:
    raise NotImplementedError


async def list_participants(pool, ticket_id: str) -> List[Any]:
    raise NotImplementedError
