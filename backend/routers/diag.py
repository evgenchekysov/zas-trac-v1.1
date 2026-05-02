from fastapi import APIRouter, Depends
from core.deps import get_current_user_id
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/diag", tags=["diagnostics"])

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

@router.get("/whoami")
async def whoami(
    user_id: str = Depends(get_current_user_id),
):
    return {"user_id": user_id}


# -------------------------------------------------
# OPEN DISPATCHER UI
# -------------------------------------------------


@router.get("/dispatcher", response_class=HTMLResponse)
def open_dispatcher():
    return """
    <html>
    <body style="font-family: Arial; padding: 30px;">
        <h2>Dispatcher</h2>
        <a href="/static/tickets-dispatcher.html" target="_blank">
            <button style="padding:10px 20px; font-size:16px;">
                Открыть диспетчер
            </button>
        </a>
    </body>
    </html>
    """
