from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import tickets, sessions, assets, diag

app = FastAPI(title="ZAS-TRAC API")

# Static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(diag.router)
app.include_router(tickets.router)
app.include_router(sessions.router)
app.include_router(assets.router)
