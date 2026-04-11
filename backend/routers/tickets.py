from uuid import UUID
from fastapi import APIRouter, Depends

from core.deps import get_current_user_id
from services.ticket_service import ticket_service

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

# -------------------------------------------------
# CREATE TICKET
# -------------------------------------------------

@router.post("/")
async def create_ticket(
    user_id: str = Depends(get_current_user_id),
):
    """
    Создание заявки.
    creator фиксируется автоматически.
    Статус: NEW
    """

    ticket = await ticket_service.create_ticket(
        creator_id=user_id
    )

    return ticket


# -------------------------------------------------
# LIST TICKETS
# -------------------------------------------------

@router.get("/")
async def list_tickets(
    user_id: str = Depends(get_current_user_id),
):
    """
    Список доступных заявок.
    Фильтрация прав — через Supabase RLS.
    """

    return await ticket_service.list_tickets()


# -------------------------------------------------
# GET TICKET DETAILS
# -------------------------------------------------

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    """
    Детали заявки.
    Права доступа — через Supabase RLS.
    """

    ticket = await ticket_service.get_ticket(ticket_id)
    return ticket


# -------------------------------------------------
# JOIN TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/join")
async def join_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    """
    Присоединиться к заявке как participant.
    """

    await ticket_service.join_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"joined": True}


# -------------------------------------------------
# LEAVE TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/leave")
async def leave_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    """
    Выйти из заявки (перестать быть participant).
    """

    await ticket_service.leave_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"left": True}


# -------------------------------------------------
# MARK DONE
# -------------------------------------------------

@router.post("/{ticket_id}/done")
async def mark_ticket_done(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    """
    ✅ Работы выполнены (IN_PROGRESS → DONE)
    Может выполнить любой participant.
    """

    await ticket_service.mark_done(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"status": "DONE"}


# -------------------------------------------------
# CLOSE TICKET
# -------------------------------------------------

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: UUID,
    user_id: str = Depends(get_current_user_id),
):
    """
    🔒 Закрыть заявку (DONE → CLOSED)
    Только owner или admin (проверяется сервисом + RLS).
    """

    await ticket_service.close_ticket(
        ticket_id=ticket_id,
        user_id=user_id,
    )

    return {"status": "CLOSED"}
