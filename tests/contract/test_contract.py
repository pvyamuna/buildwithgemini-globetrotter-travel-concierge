"""API Contract and Schema Tests for Globetrotter FastAPI Proxy & Agent Interfaces."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("AGENT_ENGINE_RESOURCE_NAME", "projects/123/locations/us-central1/reasoningEngines/456")
os.environ.setdefault("AGENT_DIRECTORY", "app")

from fastapi.testclient import TestClient
from frontend.main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_health_endpoint_contract(client):
    """Verifies GET /health endpoint contract returns status 200 and expected JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "service" in data
    assert data["service"] == "globetrotter-frontend"
    assert "resource" in data


def test_openapi_schema_contract(client):
    """Verifies OpenAPI schema contract generated at /openapi.json."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Globetrotter Travel Concierge API"
    assert "/chat" in schema["paths"]
    assert "/health" in schema["paths"]


def test_chat_endpoint_contract(client):
    """Verifies POST /chat endpoint contract receives prompt and returns parts array."""
    mock_task = MagicMock()
    mock_task.context_id = "ctx-123"
    mock_artifact = MagicMock()
    
    mock_part = MagicMock()
    mock_part.root.text = "Hello from Globetrotter!"
    mock_artifact.parts = [mock_part]
    mock_task.artifacts = [mock_artifact]

    async def mock_send_message(*args, **kwargs):
        yield (mock_task, None)

    mock_a2a_factory = MagicMock()
    mock_a2a_instance = MagicMock()
    mock_a2a_instance.send_message.side_effect = mock_send_message
    mock_a2a_factory.return_value.create.return_value = mock_a2a_instance

    with patch("frontend.main.ClientFactory", mock_a2a_factory), \
         patch("frontend.main._get_card", new_callable=AsyncMock):
        
        response = client.post(
            "/chat",
            json={"message": "Search travel packages for Tokyo", "user_id": "contract-user"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "parts" in data
        assert isinstance(data["parts"], list)
        assert len(data["parts"]) > 0
        assert data["parts"][0]["kind"] == "text"


def test_chat_error_contract(client):
    """Verifies API error contract always returns structured JSON instead of raw 500 HTML."""
    with patch("frontend.main._get_card", side_effect=Exception("Backend engine unreachable")):
        response = client.post(
            "/chat",
            json={"message": "Trigger error"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "parts" in data
        assert len(data["parts"]) > 0
        assert "Error" in data["parts"][0]["text"]
