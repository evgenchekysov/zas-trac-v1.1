from supabase import create_client
from fastapi import Header, HTTPException
from core.settings import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)

    token = authorization.removeprefix("Bearer ").strip()

    resp = supabase.auth.get_user(token)
    if not resp.user:
        raise HTTPException(status_code=401)

    return resp.user
