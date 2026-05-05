"""FedLens FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fedlens.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title="FedLens",
        description="Fed Communication Intelligence Engine",
        version="0.1.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include routers
    from api.routers.health import router as health_router
    from api.routers.documents import router as documents_router
    from api.routers.search import router as search_router
    from api.routers.event_study import router as event_study_router
    from api.routers.briefing import router as briefing_router
    from api.routers.review import router as review_router
    from api.routers.sentiment import router as sentiment_router

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(documents_router, prefix="/api/v1")
    application.include_router(search_router, prefix="/api/v1")
    application.include_router(event_study_router, prefix="/api/v1")
    application.include_router(briefing_router, prefix="/api/v1")
    application.include_router(review_router, prefix="/api/v1")
    application.include_router(sentiment_router, prefix="/api/v1")

    return application


app = create_app()
