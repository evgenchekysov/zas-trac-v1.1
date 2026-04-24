from fastapi import Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client
from core.config import settings

security = HTTPBearer()

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    token = credentials.credentials

    res = supabase.auth.get_user(token)
    if not res or not res.user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return res.user.id
