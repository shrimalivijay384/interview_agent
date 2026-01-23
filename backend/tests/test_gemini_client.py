"""
Unit tests for Gemini client.
"""
import pytest
from app.services.gemini_client import GeminiClient, get_gemini_client


class TestGeminiClient:
    """Test suite for Gemini client."""
    
    def test_client_initialization(self):
        """Test that client initializes correctly."""
        client = get_gemini_client()
        assert client is not None
        assert client.model_name is not None
    
    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat functionality."""
        client = get_gemini_client()
        response = await client.chat(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'hello' and nothing else."
        )
        assert response is not None
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_chat_with_json_response(self):
        """Test JSON response parsing."""
        client = get_gemini_client()
        response = await client.chat_with_json_response(
            system_prompt="You are a JSON generator.",
            user_prompt='Return this JSON: {"status": "ok", "value": 42}'
        )
        assert isinstance(response, dict)
        # Note: Actual response may vary, so we just check it's a dict


# TODO: Add more comprehensive tests
# - Test error handling
# - Test different temperature settings
# - Test token limits
# - Mock API calls for faster testing
