from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    database_url: str = "sqlite:///./vectorvault.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "unsafe-development-secret-change-me"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    vector_store: str = "local"
    embedding_provider: str = "local"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    pinecone_api_key: str | None = None
    pinecone_index: str | None = None
    cors_origins: str = "http://localhost:3000"
    max_upload_bytes: int = 10 * 1024 * 1024
    max_top_k: int = 20

@lru_cache
def settings() -> Settings: return Settings()
