# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Tell pydantic-settings where to load env vars from
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # General app settings
    APP_NAME: str = "Conversation Backend Service"
    APP_VERSION: str = "0.1.0"

    # LLM settings (we'll use later)
    LLM_API_KEY: str | None = None
    LLM_MODEL_NAME: str = "dummy-model"


settings = Settings()