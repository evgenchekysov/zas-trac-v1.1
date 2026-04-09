from fastapi import APIRouter, Depends
from core.deps import get_current_user_id

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)

# Эндпоинты будут добавлены позже (admin-only, через RLS)
