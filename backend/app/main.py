"""
LinguaChat Backend — FastAPI Application Entry Point

This is the application foundation only.
Full features (auth, rooms, websocket, translation) are implemented
by individual team members per their assigned tasks.
"""

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
