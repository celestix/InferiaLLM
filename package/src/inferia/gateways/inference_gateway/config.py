"""
Configuration for Inference Gateway.
"""

from typing import Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Inference Gateway settings."""

    # Application Settings
    app_name: str = "InferiaLLM Inference Gateway"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    log_level: str = "INFO"

    # Filtration Gateway Settings
    filtration_gateway_url: str = "http://localhost:8000"
    filtration_internal_key: str = Field(
        default="dev-internal-key-change-in-prod",
        alias="INTERNAL_API_KEY",
        validation_alias="INTERNAL_API_KEY",
    )

    # CORS Settings
    # In production, set ALLOWED_ORIGINS to specific domains (comma-separated)
    # Example: "https://app.inferia.ai,https://admin.inferia.ai"
    # Default is restrictive - only allow localhost origins
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8001",
        alias="ALLOWED_ORIGINS",
        validation_alias="ALLOWED_ORIGINS",
    )

    # Timeouts
    request_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars from shared .env file
    )


settings = Settings()
