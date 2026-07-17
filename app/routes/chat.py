"""Chat API routes.

POST /api/chat          — full response
POST /api/chat/stream   — SSE token stream

No business logic here — all work is delegated to ``chat_service``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse
from app.security import limiter
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a chat message and receive a full AI response",
)
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """Handle a fan chat message and return the AI response.

    Args:
        request: FastAPI request (needed by rate limiter).
        body: Validated ChatRequest with message, language, stadium_id.

    Returns:
        ChatResponse with the AI reply.
    """
    reply = await chat_service.get_chat_response(
        message=body.message,
        language=body.language,
        stadium_id=body.stadium_id,
    )
    return ChatResponse(
        reply=reply,
        language=body.language,
        stadium=body.stadium_id,
    )


@router.post(
    "/stream",
    summary="Stream a chat response via Server-Sent Events",
)
@limiter.limit("30/minute")
async def chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    """Stream the AI response token-by-token for real-time display.

    Args:
        request: FastAPI request (needed by rate limiter).
        body: Validated ChatRequest.

    Returns:
        StreamingResponse with text/event-stream content type.
    """

    async def event_generator() -> AsyncIterator[str]:
        """Yield SSE-formatted token events."""
        async for token in chat_service.stream_chat_response(
            message=body.message,
            language=body.language,
            stadium_id=body.stadium_id,
        ):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
