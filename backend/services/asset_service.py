"""
ZAS-TRAC — Asset Service
=======================

Сервис работы с оборудованием и его связью с заявками.
"""

async def assign_asset(ticket_id: str, asset_id: str):
    raise NotImplementedError


async def unassign_asset(ticket_id: str, asset_id: str):
    raise NotImplementedError


async def list_ticket_assets(ticket_id: str):
    raise NotImplementedError
