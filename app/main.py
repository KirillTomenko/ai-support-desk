from fastapi import FastAPI

from app.api.routes.analyze import router as analyze_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    configure_logging()
    Base.metadata.create_all(bind=engine)

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
