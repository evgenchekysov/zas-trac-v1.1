from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ✅ APP
app = FastAPI(title="ZAS-TRAC API")

# ✅ LOGGER
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔥 {request.method} {request.url}")

    response = await call_next(request)

    print(f"✅ {request.method} {request.url} -> {response.status_code}")
    return response


# ✅ CORS (оставляем, но фактически уже не нужен благодаря одному origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTERS
from routers import tickets
from routers import sessions
from routers import assets
from routers import diag

app.include_router(diag.router)
app.include_router(tickets.router)
app.include_router(sessions.router)
app.include_router(assets.router)

# ✅ СТАТИКА (assets только!)
app.mount(
    "/assets",
    StaticFiles(directory="../frontend/dist/assets"),
    name="assets"
)

# ✅ SPA fallback (ключевой момент!)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("../frontend/dist/index.html")