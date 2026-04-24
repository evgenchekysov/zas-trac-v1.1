from uuid import UUID
from fastapi import APIRouter, Depends

from core.deps import get_current_user_id
from services.session_workflow import Session_Workflow

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)

@router.post("/start/{ticket_id}")
async def start_session(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    session = await Session_Workflow.start_session(
        user_id=user_id,
        ticket_id=ticket_id,
    )
    return session

@router.post("/stop")
async def stop_active_session(
    user_id: str = Depends(get_current_user_id),
):
    active = await Session_Workflow.stop_session(user_id)
    return {"stopped": active is not None}

