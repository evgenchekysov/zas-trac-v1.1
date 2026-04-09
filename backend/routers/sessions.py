from fastapi import APIRouter, Depends
from core.deps import get_current_user_id

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)

# Эндпоинты будут добавлены в День 30
