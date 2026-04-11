from fastapi import APIRouter, Depends
from core.deps import get_current_user_id
from services.user_service import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
async def get_me(
    user_id: str = Depends(get_current_user_id),
):
    """
    Текущий пользователь.
    """
    return await user_service.get_user(user_id)


@router.get("/")
async def list_users(
    user_id: str = Depends(get_current_user_id),
):
    """
    Список пользователей.
    Доступ контролируется Supabase RLS (admin / worker).
    """
    return await user_service.list_users()
