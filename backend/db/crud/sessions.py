"""
Work sessions CRUD.

Day 29/early Day 30:
- structure only
- time logic comes later
"""

from typing import Any, List
from datetime import datetime


async def start_session(
    pool,
    ticket_id: str,
    user_id: str,
    started_at: datetime | None = None,
) -> Any:
    raise NotImplementedError


async def stop_session(
    pool,
    session_id: str,
    finished_at: datetime | None = None,
) -> None:
    raise NotImplementedError


async def list_sessions_by_ticket(
    pool,
    ticket_id: str,
) -> List[Any]:
    raise NotImplementedError


async def get_active_session(
    pool,
    ticket_id: str,
    user_id: str,
) -> Any | None:
    raise NotImplementedError
