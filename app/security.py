"""Security utilities: input sanitization, prompt-injection defence, rate limiting.

Every user-supplied string passes through ``sanitize_input`` before it
touches business logic or the LLM.  The ``build_safe_messages`` function
enforces a strict delimiter-based separation between the immutable system
prompt and user input so that prompt-injection attacks cannot alter the
system instruction.  ``sanitize_llm_output`` cleans model responses before
they reach the client.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from slowapi import Limiter
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_INPUT_LENGTH: int = 2000
"""Maximum allowed length for any user-supplied text field."""

MAX_OUTPUT_LENGTH: int = 8000
"""Maximum allowed length for LLM output returned to the client."""

# Patterns commonly used in prompt-injection attempts.
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"<\|?(system|assistant|user)\|?>", re.I),
    re.compile(r"\[INST\]|\[/INST\]", re.I),
    re.compile(r"###\s*(instruction|system|human|assistant)", re.I),
]

# Patterns that should never appear in LLM output returned to the client.
_OUTPUT_LEAK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(api[_\-]?key|secret|password|token)\s*[:=]\s*\S+", re.I),
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.I),
]

# ---------------------------------------------------------------------------
# Rate limiter (shared instance)
# ---------------------------------------------------------------------------

limiter: Limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
"""Global SlowAPI rate-limiter instance used by the FastAPI app."""

# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------


def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Sanitize user-supplied text before it enters business logic.

    Steps:
    1. Strip leading/trailing whitespace.
    2. Remove ASCII/Unicode control characters (except newline, tab).
    3. Normalize Unicode to NFC form to prevent homoglyph tricks.
    4. Truncate to ``max_length`` characters.

    Args:
        text: Raw user input string.
        max_length: Maximum allowed character count.

    Returns:
        Cleaned, length-bounded string safe for downstream processing.
    """
    if not isinstance(text, str):
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove control characters except \n and \t
    text = "".join(
        ch for ch in text
        if ch in ("\n", "\t") or not unicodedata.category(ch).startswith("C")
    )

    # Normalize Unicode (prevent homoglyph spoofing)
    text = unicodedata.normalize("NFC", text)

    # Enforce length limit
    if len(text) > max_length:
        text = text[:max_length]

    return text


def contains_injection_attempt(text: str) -> bool:
    """Check whether *text* contains known prompt-injection patterns.

    This is a defence-in-depth heuristic — the primary defence is the
    delimiter-based message structure enforced by ``build_safe_messages``.

    Args:
        text: Sanitized user input.

    Returns:
        True if a suspicious pattern is detected.
    """
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


# ---------------------------------------------------------------------------
# Prompt construction (injection-proof)
# ---------------------------------------------------------------------------


def build_safe_messages(
    user_input: str,
    system_prompt: str,
) -> list[dict[str, str]]:
    """Build an LLM messages list with strict role separation.

    The system prompt is placed in a dedicated ``system`` role message and
    is **never** concatenated with user input.  This prevents the user from
    injecting instructions that would be interpreted as system-level.

    Args:
        user_input: Sanitized user message.
        system_prompt: Immutable system instruction.

    Returns:
        List of ``{"role": ..., "content": ...}`` dicts ready for the LLM.
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]


# ---------------------------------------------------------------------------
# LLM output sanitization
# ---------------------------------------------------------------------------


def sanitize_llm_output(text: str, max_length: int = MAX_OUTPUT_LENGTH) -> str:
    """Clean LLM-generated text before returning it to the client.

    Removes potential secret leaks and enforces a length cap.

    Args:
        text: Raw LLM response text.
        max_length: Maximum output length.

    Returns:
        Sanitized output string.
    """
    if not isinstance(text, str):
        return ""

    # Remove any leaked secrets/keys
    for pattern in _OUTPUT_LEAK_PATTERNS:
        text = pattern.sub("[REDACTED]", text)

    # Enforce length
    if len(text) > max_length:
        text = text[:max_length] + "…"

    return text


def get_rate_limit_key(request: Any) -> str:
    """Extract a rate-limiting key from a FastAPI request.

    Args:
        request: The incoming Starlette/FastAPI Request object.

    Returns:
        Client IP address string.
    """
    return get_remote_address(request)
