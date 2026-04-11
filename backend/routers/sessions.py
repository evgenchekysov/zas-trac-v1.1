from uuid import UUID
from fastapi import APIRouter, Depends

from core.deps import get_current_user_id
from services.session_service import session_service
from services.ticket_service import ticket_service

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


@router.post("/start/{ticket_id}")
async def start_session(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    session = await session_service.start_session(
        user_id=user_id,
        ticket_id=ticket_id,
    )

    # статус = агрегат сессий
    await ticket_service.recalc_status(ticket_id)

    return session


@router.post("/stop")
async def stop_active_session(
    user_id: str = Depends(get_current_user_id),
):
    active = await session_service.stop_active_session(user_id)

    if active:
        await ticket_service.recalc_status(active.ticket_id)

    return {"stopped": active is not None}
``
