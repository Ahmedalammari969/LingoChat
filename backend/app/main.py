"""
LinguaChat Backend — FastAPI Application Entry Point

This is the application foundation only.
Full features (auth, rooms, websocket, translation) are implemented
by individual team members per their assigned tasks.
"""

import mimetypes
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json", ".json")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers

app = FastAPI(
    title="LinguaChat API",
    version=settings.APP_VERSION,
    description="Real-time multilingual chat system",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Database Initialization on Startup ────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    from app.database.base import Base
    from app.database.session import engine
    # Import all models so metadata is populated
    import app.database.models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ── Routers ───────────────────────────────────────────────────────────────────
# Routers are registered here as they are implemented by team members.
# DO NOT add a router here without the corresponding implementation being done.
#
from app.auth.router import router as auth_router
from app.dashboard.router import router as dashboard_router
from app.rooms.router import router as rooms_router
from app.websocket.router import router as websocket_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(rooms_router, prefix="/api/v1/rooms", tags=["Rooms"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint. No authentication required.
    Returns basic application status.
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }


# ── Serve Built Frontend (Single Unified Port) ─────────────────────────────────
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws") or full_path.startswith("health") or full_path.startswith("docs"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")

        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
