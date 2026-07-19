"""Tests for google-sdk LLM client."""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import get_settings
from app.llm.client import generate, generate_stream


@pytest.fixture(autouse=True)
def setup_google_sdk() -> None:
    settings = get_settings()
    settings.llm_provider = "google-sdk"
    settings.llm_api_key = "test_google_key"

    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_google.genai = mock_genai
    sys.modules["google"] = mock_google
    sys.modules["google.genai"] = mock_genai
    sys.modules["google.genai.types"] = MagicMock()

    yield

    del sys.modules["google"]
    del sys.modules["google.genai"]
    del sys.modules["google.genai.types"]


@pytest.mark.asyncio
async def test_google_sdk_generate() -> None:
    """Test google-sdk generate."""
    mock_genai = sys.modules["google.genai"]
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "Hello from Google"

    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    result = await generate("prompt", "system")
    assert result == "Hello from Google"
    mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_google_sdk_generate_stream() -> None:
    """Test google-sdk generate_stream."""
    mock_genai = sys.modules["google.genai"]
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client

    mock_chunk = MagicMock()
    mock_chunk.text = "chunk"

    async def mock_generate_content_stream(*args: object, **kwargs: object):
        yield mock_chunk

    mock_client.aio.models.generate_content_stream = mock_generate_content_stream

    chunks = []
    async for c in generate_stream("prompt", "system"):
        chunks.append(c)

    assert chunks == ["chunk"]
