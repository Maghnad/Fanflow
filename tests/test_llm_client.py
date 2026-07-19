import pytest
from unittest.mock import patch, MagicMock
from app.llm.client import generate, generate_stream
from app.config import get_settings

@pytest.mark.asyncio
async def test_llm_client_openai():
    settings = get_settings()
    settings.llm_provider = "openai"
    settings.llm_api_key = "test_key"
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }
        mock_post.return_value = mock_response
        
        result = await generate("system", "user")
        assert result == "Hello!"

@pytest.mark.asyncio
async def test_llm_client_openai_error():
    settings = get_settings()
    settings.llm_provider = "openai"
    settings.llm_api_key = "test_key"
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("API error")
        result = await generate("system", "user", use_cache=False)
        assert result == "I'm FanFlow AI, your FIFA World Cup 2026 stadium assistant. I'm currently unable to connect to my AI backend. Please try again shortly, or ask a staff member for help."

@pytest.mark.asyncio
async def test_llm_client_stream_openai():
    settings = get_settings()
    settings.llm_provider = "openai"
    settings.llm_api_key = "test_key"
    
    async def mock_aiter():
        yield 'data: {"choices": [{"delta": {"content": "Hi"}}]}\n\n'
        yield 'data: [DONE]\n\n'
        
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter
        mock_context.__aenter__.return_value = mock_response
        mock_stream.return_value = mock_context
        
        chunks = []
        async for chunk in generate_stream("system", "user"):
            chunks.append(chunk)
            
        assert chunks == ["Hi"]
