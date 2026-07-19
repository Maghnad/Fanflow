"""Shared test fixtures.

Provides a mock LLM client and a TestClient with the mock injected,
so tests never hit the real LLM API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Generator

# ---------------------------------------------------------------------------
# Mock LLM responses
# ---------------------------------------------------------------------------

MOCK_CHAT_RESPONSE: str = (
    "Welcome to MetLife Stadium! The nearest restroom is located on the "
    "North Concourse, about 30 meters from Gate A. Follow the signs marked "
    "'Restrooms' after entering the concourse."
)

MOCK_ANALYSIS_RESPONSE: str = (
    "The overall crowd density is moderate at approximately 55%. "
    "Gate A is experiencing higher congestion than other gates.\n\n"
    "1. Consider redirecting fans from Gate A to Gate C which has lower congestion.\n"
    "2. Deploy additional staff to Gate A to manage flow.\n"
    "3. Activate overflow parking signage for Lot K.\n"
    "4. Monitor Gate B which is approaching yellow-level congestion.\n"
    "5. Prepare medical team for standby given current crowd size."
)


# ---------------------------------------------------------------------------
# Mock LLM generate functions
# ---------------------------------------------------------------------------


async def mock_generate(
    prompt: str,
    system: str,
    *,
    settings: Any = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> str:
    """Mock LLM generate that returns deterministic responses.

    Args:
        prompt: User prompt (used to detect analysis vs chat).
        system: System prompt.
        settings: Ignored.
        use_cache: Ignored.
        **kwargs: Ignored.

    Returns:
        Deterministic mock response string.
    """
    if "crowd" in prompt.lower() or "density" in prompt.lower():
        return MOCK_ANALYSIS_RESPONSE
    return MOCK_CHAT_RESPONSE


async def mock_generate_stream(
    prompt: str,
    system: str,
    *,
    settings: Any = None,
    **kwargs: Any,
) -> AsyncIterator[str]:
    """Mock LLM streaming that yields tokens from the mock response.

    Args:
        prompt: User prompt.
        system: System prompt.
        settings: Ignored.
        **kwargs: Ignored.

    Yields:
        Individual words from the mock response.
    """
    words = MOCK_CHAT_RESPONSE.split(" ")
    for word in words:
        yield word + " "


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Create a TestClient with mock LLM injected.

    Returns:
        FastAPI TestClient instance.
    """
    with (
        patch("app.llm.client.generate", side_effect=mock_generate),
        patch("app.llm.client.generate_stream", side_effect=mock_generate_stream),
        patch("app.llm.client.close_http_client", new_callable=AsyncMock),
        patch("app.services.chat_service.llm_client") as mock_llm,
        patch("app.services.crowd_service.llm_client") as mock_crowd_llm,
    ):
        mock_llm.generate = AsyncMock(side_effect=mock_generate)
        mock_llm.generate_stream = mock_generate_stream
        mock_crowd_llm.generate = AsyncMock(side_effect=mock_generate)
        mock_crowd_llm.generate_stream = mock_generate_stream

        from app.main import app

        with TestClient(app) as test_client:
            yield test_client
