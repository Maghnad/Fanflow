"""FastAPI application factory.

Creates the app with CORS, rate limiting, static file serving, and all
route inclusions.  Uses lifespan context manager for startup/shutdown
of the shared HTTP client.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.llm.client import close_http_client
from app.routes import chat, crowd, navigation, static_pages
from app.security import limiter

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    On startup: log configuration summary.
    On shutdown: close the shared LLM HTTP client.

    Args:
        app: The FastAPI application instance.
    """
    settings = get_settings()
    logger.info("FanFlow AI starting up...")
    logger.info("LLM Provider: %s | Model: %s", settings.llm_provider, settings.llm_model)
    logger.info(
        "API key configured: %s",
        "Yes" if settings.llm_api_key and settings.llm_api_key != "your-api-key-here" else "No",
    )
    yield
    logger.info("FanFlow AI shutting down...")
    await close_http_client()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="FanFlow AI",
        description=(
            "GenAI-enabled stadium operations solution for the FIFA World Cup 2026. "
            "Provides multilingual fan assistance and real-time crowd intelligence."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── Rate limiting ──────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # ── CORS ───────────────────────────────────────────────────────────
    allowed_origins = [
        origin.strip()
        for origin in settings.allowed_origins.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ── Static files ───────────────────────────────────────────────────
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # ── Routes ─────────────────────────────────────────────────────────
    app.include_router(static_pages.router)
    app.include_router(chat.router)
    app.include_router(navigation.router)
    app.include_router(crowd.router)

    return app


# Create the app instance for uvicorn
app: FastAPI = create_app()
