from typing import Optional, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChromaConfig(BaseModel):
    api_key: Optional[str] = None
    tenant: Optional[str] = None
    url: Optional[str] = None
    is_local: bool = True
    database: Optional[str] = None


class VectorDBConfig(BaseModel):
    chroma: ChromaConfig = Field(default_factory=ChromaConfig)


class ProvidersConfig(BaseModel):
    vectordb: VectorDBConfig = Field(default_factory=VectorDBConfig)


class Settings(BaseSettings):
    """Data Service Settings (Includes Prompt Settings)"""

    app_name: str = "Data Service"
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)

    # Redis for caching (optional future use)
    redis_url: str = "redis://localhost:6379/0"

    # Optional OpenAI Key for Rewriting
    openai_api_key: Optional[str] = None

    # Control Plane Connection
    filtration_url: str = Field(
        default="http://localhost:8000", validation_alias="FILTRATION_URL"
    )
    internal_api_key: str = Field(default="", validation_alias="INTERNAL_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


settings = Settings()
