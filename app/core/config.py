from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "Conversation Backend Service"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str = "sqlite:///./app.db" 
  
    LLM_PROVIDER: str = "dummy" 
    LLM_API_KEY: str | None = None
    LLM_MODEL_NAME: str = "dummy-model"

    MAX_HISTORY_MESSAGES: int = 10   
    MAX_CONTEXT_CHARS: int = 4000  
    
settings = Settings()