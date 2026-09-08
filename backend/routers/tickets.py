from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import create_client

from core.config import settings
from core.deps import get_current_user_id

from services import ticket_workflow

from domain.ticket import TicketPriority


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


# ✅ ВАЖНО: service key вместо anon
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY,
)


# -------------------------------------------------
# DTO
# -------------------------------------------------

class PriorityRequest(BaseModel):
    priority: str


# -------------------------------------------------
# CREATE TICKET
# -------------------------------------------------

@router.post("/")
async def create_ticket(data: dict):
    try:
        res = supabase.table("tickets").insert(
            {
                "description": data.get("description"),
                "status": "NEW",
                "asset_qr": data.get("asset_qr"),
            }
        ).execute()

        return res.data

    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------
# LIST TICKETS
# -------------------------------------------------

@router.get("/")
async def list_tickets(
    user_id: str = Depends(get_current_user_id),
):
    res = (
        supabase.table("tickets")
        .select(
            """
            id,
            description,
            status,
            priority,
            priority_state,
            asset_qr,
            assets (
                name,
                location
            )
            """
        )
        .order("id", desc=True)
        .execute()
    )

    return res.data


# -------------------------------------------------
# GET TICKET DETAILS
# -------------------------------------------------

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """
    Детали заявки.
    Права доступа — через Supabase RLS.
    """

    ticket = await ticket_workflow.get_ticket(ticket_id)

    return ticket


# -------------------------------------------------
# JOIN TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/join")
async def join_ticket(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.join_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"joined": True}


# -------------------------------------------------
# LEAVE TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/leave")
async def leave_ticket(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.leave_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"left": True}


# -------------------------------------------------
# MARK DONE
# -------------------------------------------------

@router.post("/{ticket_id}/done")
async def mark_ticket_done(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.mark_done(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"status": "DONE"}


# -------------------------------------------------
# CLOSE TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.close_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
        is_admin=False,  # временно
    )

    return {"status": "CLOSED"}


# -------------------------------------------------
# CHANGE PRIORITY
# ADR‑008 Foundation
# -------------------------------------------------

@router.post("/{ticket_id}/priority")
async def change_priority(
    ticket_id: int,
    data: PriorityRequest,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.change_priority(
        ticket_id=ticket_id,
        priority=TicketPriority(data.priority),
        user_id=user_id,
    )

    return {
        "priority": data.priority,
    }


# -------------------------------------------------
# LOCK PRIORITY
# ADR‑008 Foundation
# -------------------------------------------------

@router.post("/{ticket_id}/priority/lock")
async def lock_priority(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.lock_priority(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {
        "priority_state": "LOCKED",
    }


# -------------------------------------------------
# START TICKET SESSION
# -------------------------------------------------

@router.post("/{ticket_id}/start")
async def start_session(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.start_session(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"started": True}


# -------------------------------------------------
# STOP TICKET SESSION
# -------------------------------------------------

@router.post("/{ticket_id}/stop")
async def stop_session(
    ticket_id: int,
    user_id: str = Depends(get_current_user_id),
):
    await ticket_workflow.stop_session(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"stopped": True}
