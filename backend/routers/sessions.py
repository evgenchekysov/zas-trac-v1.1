from uuid import UUID
from services import session_workflow
from fastapi import APIRouter, Depends
from core.deps import get_current_user_id

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)

@router.post("/start/{ticket_id}")
async def start_session(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    session = await session_workflow.start_session(
        user_id=user_id,
        ticket_id=ticket_id,
    )
    return session

@router.post("/stop")
async def stop_active_session(
    user_id: str = Depends(get_current_user_id),
):
    active = await session_workflow.stop_session(user_id)
    return {"stopped": active is not None}

