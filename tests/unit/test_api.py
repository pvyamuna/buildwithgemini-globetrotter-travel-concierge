import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app import GlobetrotterClient, run_agent_query


def test_globetrotter_client_tools_list():
    client = GlobetrotterClient()
    tools = client.list_available_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert "search_travel_packages" in tools


@pytest.mark.asyncio
async def test_async_query_mocked():
    client = GlobetrotterClient(user_id="test-user")
    
    mock_session = MagicMock()
    mock_session.session_id = "test-session-123"
    
    mock_event = MagicMock()
    mock_event.content.parts = [MagicMock(text="Tokyo is wonderful!")]
    
    async def mock_run_async(*args, **kwargs):
        yield mock_event

    with patch.object(client.session_service, "get_session", new_callable=AsyncMock, return_value=mock_session), \
         patch.object(client.runner, "run_async", side_effect=mock_run_async):
        
        result = await client.async_query("What to visit in Tokyo?")
        
        assert result["status"] == "success"
        assert "Tokyo is wonderful!" in result["text"]
        assert result["session_id"] == "test-session-123"


def test_run_agent_query_mocked():
    mock_session = MagicMock()
    mock_session.session_id = "sync-session-456"
    
    mock_event = MagicMock()
    mock_event.content.parts = [MagicMock(text="Bali beaches are serene.")]
    
    async def mock_run_async(*args, **kwargs):
        yield mock_event

    with patch("google.adk.sessions.InMemorySessionService.get_session", new_callable=AsyncMock, return_value=mock_session), \
         patch("google.adk.runners.Runner.run_async", side_effect=mock_run_async):
        
        result = run_agent_query("Tell me about Bali", user_id="sync-user")
        
        assert result["status"] == "success"
        assert "Bali beaches are serene." in result["text"]
