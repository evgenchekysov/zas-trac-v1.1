# backend/core/deps.py
from fastapi import HTTPException, Request

async def get_current_user_id(request: Request) -> str:
    """
    Единственный стандарт идентификации пользователя.

    user_id извлекается из Supabase JWT (auth.uid).
    frontend / bot НЕ передают user_id явно.
    """
    user = getattr(request.state, "user", None)

    if not user or "sub" not in user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user["sub"]
