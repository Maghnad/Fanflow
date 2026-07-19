"""Application configuration loaded from environment variables.

Uses pydantic-settings to provide typed, validated configuration with
sensible defaults. All secrets (API keys) are read from environment
variables or a .env file — never hardcoded.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Typed application settings sourced from environment variables.

    Attributes:
        llm_provider: LLM provider identifier (e.g. 'openai', 'google').
        llm_model: Model name to request from the provider.
        llm_api_key: Secret API key — never expose to the frontend.
        llm_base_url: Base URL for the LLM API (OpenAI-compatible).
        allowed_origins: Comma-separated CORS origin allowlist.
        rate_limit: Max requests per minute per IP address.
        app_env: Runtime environment ('development' or 'production').
        log_level: Logging verbosity level.
    """

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    rate_limit: int = 60
    app_env: str = "development"
    log_level: str = "info"

    # GCP Integrations
    gcp_project_id: str = ""
    use_secret_manager: bool = False
    gcp_secret_name: str = "fanflow-llm-api-key"
    use_firestore: bool = False
    gcp_maps_api_key: str = ""

    class Config:
        """Pydantic-settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Create and return a cached Settings instance.

    If use_secret_manager is True, this fetches the LLM_API_KEY from
    Google Cloud Secret Manager at startup, overriding the local .env value.

    Returns:
        Validated Settings populated from environment variables/Secret Manager.
    """
    settings = Settings()

    if settings.use_secret_manager and settings.gcp_project_id:
        try:
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{settings.gcp_project_id}/secrets/{settings.gcp_secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            settings.llm_api_key = secret_value
            logger.info("Successfully fetched LLM_API_KEY from Google Cloud Secret Manager.")
        except Exception as e:
            logger.error(f"Failed to fetch secret from GCP Secret Manager: {e}")
            # Will gracefully fall back to the env variable if it exists

    return settings
