"""
Assets CRUD.

Day 29/early Day 30:
- admin-oriented
- no access rules here (RLS responsibility)
"""

from typing import Any, List


async def create_asset(pool, data: dict) -> Any:
    raise NotImplementedError


async def get_asset_by_id(pool, asset_id: str) -> Any:
    raise NotImplementedError


async def list_assets(pool) -> List[Any]:
    raise NotImplementedError


async def update_asset(pool, asset_id: str, data: dict) -> None:
    raise NotImplementedError


async def delete_asset(pool, asset_id: str) -> None:
    raise NotImplementedError
