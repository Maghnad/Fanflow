import pytest
from app.config import get_settings

def test_get_settings():
    settings = get_settings()
    assert settings.llm_provider in ["google", "openai", "groq"]
    assert settings.llm_model != ""
    assert isinstance(settings.llm_api_key, str)

def test_cors_origins():
    settings = get_settings()
    origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
    assert len(origins) >= 1
