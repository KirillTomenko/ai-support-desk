from fastapi import FastAPI

from app.api.routes.analyze import router as analyze_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.init_db import init_db


def create_app() -> FastAPI:
    configure_logging()
    init_db()

    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered support inbox analysis API.",
    )

    application.include_router(analyze_router)

    @application.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
