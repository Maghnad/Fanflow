"""Provider-agnostic LLM client.

This is the **only** module that communicates with an external LLM API.
Every other part of the application calls ``generate`` or
``generate_stream`` — never the provider SDK directly.

Swapping providers means editing this one file.  The client reads
``LLM_PROVIDER``, ``LLM_MODEL``, ``LLM_API_KEY``, and ``LLM_BASE_URL``
from environment variables (via ``app.config.Settings``).

All user input is sanitized and prompt-injection-guarded by
``app.security`` *before* reaching the LLM.  LLM output is sanitized
before being returned to callers.
"""

from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING

import httpx

from app.config import Settings, get_settings
from app.security import (
    build_safe_messages,
    contains_injection_attempt,
    sanitize_input,
    sanitize_llm_output,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LRU cache for non-streaming responses
# ---------------------------------------------------------------------------

_LRU_MAX_SIZE: int = 256
_response_cache: OrderedDict[str, str] = OrderedDict()


def _cache_key(prompt: str, system: str, model: str) -> str:
    """Generate a deterministic cache key for a prompt/system/model triple.

    Args:
        prompt: The user prompt string.
        system: The system prompt string.
        model: The model identifier.

    Returns:
        SHA-256 hex digest string.
    """
    raw = f"{model}::{system}::{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> str | None:
    """Retrieve a cached response, updating recency.

    Args:
        key: Cache key from ``_cache_key``.

    Returns:
        Cached response string or None.
    """
    if key in _response_cache:
        _response_cache.move_to_end(key)
        return _response_cache[key]
    return None


def _cache_put(key: str, value: str) -> None:
    """Store a response in the LRU cache, evicting oldest if full.

    Args:
        key: Cache key.
        value: Response text.
    """
    _response_cache[key] = value
    _response_cache.move_to_end(key)
    while len(_response_cache) > _LRU_MAX_SIZE:
        _response_cache.popitem(last=False)


# ---------------------------------------------------------------------------
# Shared httpx client (created lazily, closed on shutdown)
# ---------------------------------------------------------------------------

_http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Return the shared async HTTP client, creating it if needed.

    Returns:
        An ``httpx.AsyncClient`` instance.
    """
    global _http_client  # noqa: PLW0603
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
    return _http_client


async def close_http_client() -> None:
    """Close the shared HTTP client (called on app shutdown)."""
    global _http_client  # noqa: PLW0603
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


# ---------------------------------------------------------------------------
# Fallback response
# ---------------------------------------------------------------------------

_FALLBACK_RESPONSE: str = (
    "I'm FanFlow AI, your FIFA World Cup 2026 stadium assistant. "
    "I'm currently unable to connect to my AI backend. "
    "Please try again shortly, or ask a staff member for help."
)

_INJECTION_BLOCKED_RESPONSE: str = (
    "I'm sorry, but I couldn't process that request. "
    "Please rephrase your question about the stadium or event."
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate(
    prompt: str,
    system: str,
    *,
    settings: Settings | None = None,
    use_cache: bool = True,
    **kwargs: object,
) -> str:
    """Send a prompt to the configured LLM and return the full response.

    The prompt is sanitized, checked for injection attempts, and wrapped
    in a safe message structure before being sent.  The LLM response is
    sanitized before being returned.

    Args:
        prompt: User-facing prompt text (will be sanitized).
        system: System prompt (immutable instruction to the model).
        settings: Optional pre-built Settings; uses default if None.
        use_cache: Whether to check/populate the LRU cache.
        **kwargs: Additional provider-specific parameters.

    Returns:
        Sanitized LLM response string.
    """
    settings = settings or get_settings()

    # Sanitize user input
    clean_prompt = sanitize_input(prompt)

    # Check for prompt-injection attempts
    if contains_injection_attempt(clean_prompt):
        logger.warning("Prompt injection attempt detected and blocked.")
        return _INJECTION_BLOCKED_RESPONSE

    # Check cache
    if use_cache:
        key = _cache_key(clean_prompt, system, settings.llm_model)
        cached = _cache_get(key)
        if cached is not None:
            logger.debug("LLM cache hit.")
            return cached

    # Graceful fallback if no API key
    if not settings.llm_api_key or settings.llm_api_key == "your-api-key-here":
        logger.info("No LLM API key configured — returning fallback response.")
        return _FALLBACK_RESPONSE

    # Build safe message structure
    messages = build_safe_messages(clean_prompt, system)

    # Route to Google GenAI SDK if provider is google-sdk
    raw_text: str = ""
    if settings.llm_provider == "google-sdk":
        try:
            from google import genai
            from google.genai import types
            from typing import cast

            client = genai.Client(api_key=settings.llm_api_key)
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=clean_prompt)])]
            config = types.GenerateContentConfig(
                system_instruction=system,
                temperature=cast("float | None", kwargs.get("temperature", 0.7)),
                max_output_tokens=cast("int | None", kwargs.get("max_tokens", 1024)),
            )
            response = await client.aio.models.generate_content(
                model=settings.llm_model,
                contents=contents,
                config=config,
            )
            raw_text = response.text or ""
        except Exception as e:
            logger.error(f"Google GenAI SDK call failed: {e}")
            return _FALLBACK_RESPONSE
    else:
        # Call the LLM (OpenAI-compatible endpoint)
        try:
            http_client = await get_http_client()
            response_http = await http_client.post(
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "stream": False,
                },
            )
            response_http.raise_for_status()
            data = response_http.json()
            raw_text = data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(
                f"LLM API call failed with HTTP {e.response.status_code}: {e.response.text}"
            )
            return _FALLBACK_RESPONSE
        except Exception:
            logger.exception("LLM API call failed.")
            return _FALLBACK_RESPONSE

    # Sanitize output
    result = sanitize_llm_output(raw_text)

    # Cache the result
    if use_cache:
        _cache_put(key, result)  # type: ignore[arg-type]

    return result


async def generate_stream(
    prompt: str,
    system: str,
    *,
    settings: Settings | None = None,
    **kwargs: object,
) -> AsyncIterator[str]:
    """Stream LLM response tokens via SSE-compatible async iterator.

    Sanitization is applied to the prompt before sending.  Output tokens
    are yielded as-is for low latency; final output sanitization should
    be handled by the caller if aggregating.

    Args:
        prompt: User-facing prompt text (will be sanitized).
        system: System prompt.
        settings: Optional pre-built Settings.
        **kwargs: Additional provider-specific parameters.

    Yields:
        Individual text tokens from the LLM response stream.
    """
    settings = settings or get_settings()

    # Sanitize user input
    clean_prompt = sanitize_input(prompt)

    # Check for prompt-injection attempts
    if contains_injection_attempt(clean_prompt):
        logger.warning("Prompt injection attempt blocked (stream).")
        yield _INJECTION_BLOCKED_RESPONSE
        return

    # Graceful fallback if no API key
    if not settings.llm_api_key or settings.llm_api_key == "your-api-key-here":
        yield _FALLBACK_RESPONSE
        return

    messages = build_safe_messages(clean_prompt, system)

    if settings.llm_provider == "google-sdk":
        try:
            from google import genai
            from google.genai import types
            from typing import cast

            client = genai.Client(api_key=settings.llm_api_key)
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=clean_prompt)])]
            config = types.GenerateContentConfig(
                system_instruction=system,
                temperature=cast("float | None", kwargs.get("temperature", 0.7)),
                max_output_tokens=cast("int | None", kwargs.get("max_tokens", 1024)),
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=settings.llm_model,
                contents=contents,
                config=config,
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Google GenAI SDK streaming call failed: {e}")
            yield _FALLBACK_RESPONSE
    else:
        try:
            http_client = await get_http_client()
            async with http_client.stream(
                "POST",
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "stream": True,
                },
            ) as response_http:
                response_http.raise_for_status()
                async for line in response_http.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]  # strip "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        import json

                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (ValueError, KeyError, IndexError):
                        continue
        except httpx.HTTPStatusError as e:
            logger.error(
                f"LLM streaming call failed with HTTP {e.response.status_code}: {e.response.text}"
            )
            yield _FALLBACK_RESPONSE
        except Exception:
            logger.exception("LLM streaming call failed.")
            yield _FALLBACK_RESPONSE
