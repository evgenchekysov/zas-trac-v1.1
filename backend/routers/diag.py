from fastapi import APIRouter, Depends
from core.deps import get_current_user_id

router = APIRouter(prefix="/diag", tags=["diagnostics"])

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

@router.get("/whoami")
async def whoami(
    user_id: str = Depends(get_current_user_id),
):
    return {"user_id": user_id}
