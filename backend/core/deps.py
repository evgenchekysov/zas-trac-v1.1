from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from core.config import settings

security = HTTPBearer()

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:

    token = credentials.credentials

    try:
        res = supabase.auth.get_user(token)

        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return res.user.id

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
