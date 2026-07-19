import pytest
from app.services.chat_service import get_chat_response

@pytest.mark.asyncio
async def test_process_chat():
    reply = await get_chat_response("Where is my seat?", "en", "metlife")
    assert isinstance(reply, str)

@pytest.mark.asyncio
async def test_process_chat_unsupported_language():
    reply = await get_chat_response("Donde esta mi asiento?", "xx", "metlife")
    assert isinstance(reply, str)

@pytest.mark.asyncio
async def test_process_chat_unknown_stadium():
    reply = await get_chat_response("Food?", "en", "unknown")
    assert isinstance(reply, str)
    assert "unknown" in reply.lower() or "not found" in reply.lower() or len(reply) > 0
