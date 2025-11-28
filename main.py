from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend service for chat conversations with LLM and RAG (Case Study).",
)


@app.get("/health", tags=["health"])
def health_check():
    """
    Simple health check endpoint.
    Returns service status.
    """
    return {"status": "ok", "message": "Service is up and running"}