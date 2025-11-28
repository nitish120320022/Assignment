import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import configure_logging
from app.core.error_handlers import register_exception_handlers
from app.api.conversations import router as conversations_router
from app.api.users import router as users_router
from app.api.documents import router as documents_router

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend service for chat conversations with LLM and RAG (Case Study).",
)

@app.on_event("startup")
def on_startup():
    """
    Application startup hook.
    Ensures all database tables are created.
    """
    logger.info("Starting application, ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")

@app.get("/health", tags=["health"])
def health_check():
    """
    Simple health check endpoint.
    Returns service status.
    """
    return {"status": "ok", "message": "Service is up and running"}

register_exception_handlers(app)

app.include_router(users_router)
app.include_router(documents_router)
app.include_router(conversations_router)