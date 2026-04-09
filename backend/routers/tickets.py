from fastapi import APIRouter, Depends
from core.deps import get_current_user_id

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("/")
async def create_ticket(
    user_id: str = Depends(get_current_user_id),
):
    """Создание заявки"""
    pass


@router.get("/")
async def list_tickets(
    user_id: str = Depends(get_current_user_id),
):
    """Список доступных заявок"""
    pass


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Детали заявки"""
    pass


@router.post("/{ticket_id}/status")
async def change_ticket_status(
    ticket_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Смена статуса заявки"""
    pass


@router.post("/{ticket_id}/join")
async def join_ticket(
    ticket_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Присоединиться к заявке"""
    pass


@router.post("/{ticket_id}/leave")
async def leave_ticket(
    ticket_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Выйти из заявки"""
    pass
