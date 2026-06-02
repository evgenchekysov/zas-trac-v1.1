from fastapi import APIRouter
from db.pool import get_pool

router = APIRouter(
    prefix="/api/assets",
    tags=["assets"],
)

@router.get("/")
@router.get("")
async def get_assets():
    pool = await get_pool()

    rows = await pool.fetch("""
        SELECT qr_code, name, location
        FROM assets
        ORDER BY name
    """)

    return [
        {
            "qr_code": r["qr_code"],
            "name": r["name"],
            "location": r["location"],
        }
        for r in rows
    ]