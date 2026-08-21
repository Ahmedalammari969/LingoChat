"""
LinguaChat — Application Configuration

Loads all settings from environment variables.
NEVER hardcode values here. Use .env file locally.
"""

import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    See backend/.env.example for all available variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/linguachat"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET: str = "dev-secret-key-change-in-production-32bytes-min"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Redis (Optional) ──────────────────────────────────────────────────
    # OPTIONAL: application starts without Redis (uses in-memory cache).
    # Set REDIS_URL to enable Redis-backed translation cache.
    REDIS_URL: str = ""

    # ── Translation: LibreTranslate ───────────────────────────
    LIBRETRANSLATE_URL: str = ""
    LIBRETRANSLATE_API_KEY: str = ""

    # ── Translation: Google (Optional Fallback) ───────────────
    # OPTIONAL: leave empty to disable Google fallback.
    # When set, Google is tried after LibreTranslate failure.
    # See: docs/translation-contract.md § 6. Provider Interface
    GOOGLE_TRANSLATE_API_KEY: str = ""

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Security ──────────────────────────────────────────────
    BCRYPT_ROUNDS: int = 12

    # ── WebSocket ─────────────────────────────────────────────
    WS_HEARTBEAT_TIMEOUT_SECONDS: int = 90


settings = Settings()
