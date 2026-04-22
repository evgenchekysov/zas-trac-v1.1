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

from fastapi import Request, HTTPException
from supabase import create_client
from core.config import settings

@router.get("/me_raw")
async def get_me_raw(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="No Authorization header")

    token = auth.replace("Bearer ", "")

    supabase = create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
        options={
            "global": {
                "headers": {
                    "Authorization": f"Bearer {token}"
                }
            }
        }
    )

    result = supabase.table("users").select(
        "id, full_name, role"
    ).single().execute()

    return result.data
    
