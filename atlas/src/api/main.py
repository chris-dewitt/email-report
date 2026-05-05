"""FastAPI application factory for the Atlas API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from atlas.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Atlas API",
        description="Macro Intelligence Platform — API for economic state tracking and feature monitoring",
        version="0.1.0",
    )

    # CORS for React dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from api.routers.health import router as health_router
    from api.routers.series import router as series_router
    from api.routers.features import router as features_router
    from api.routers.regime import router as regime_router
    from api.routers.copilot import router as copilot_router

    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(series_router, prefix="/api/v1", tags=["series"])
    app.include_router(features_router, prefix="/api/v1", tags=["features"])
    app.include_router(regime_router, prefix="/api/v1", tags=["regime"])
    app.include_router(copilot_router, prefix="/api/v1", tags=["copilot"])

    return app
