"""Unit tests for video generation tools."""

from unittest.mock import MagicMock, patch
from app.video_tools import (
    generate_destination_video,
    GCS_BUCKET_NAME,
    PROJECT_ID,
)


def test_video_tools_config():
    assert PROJECT_ID == "qwiklabs-gcp-01-892a42380662"
    assert GCS_BUCKET_NAME == "globetrotter-travel-media-qwiklabs-gcp-01-892a42380662"


@patch("app.video_tools.storage.Client")
@patch("app.video_tools.genai.Client")
def test_generate_destination_video_success(mock_genai_client, mock_storage_client):
    mock_gcs = MagicMock()
    mock_storage_client.return_value = mock_gcs

    mock_ai = MagicMock()
    mock_genai_client.return_value = mock_ai

    mock_interaction = MagicMock()
    mock_interaction.output_video.data = b"fake_mp4_bytes"
    mock_ai.interactions.create.return_value = mock_interaction

    mock_tool_context = MagicMock()

    url = generate_destination_video(
        "3 second drone shot of Mt. Fuji at sunrise", tool_context=mock_tool_context
    )
    assert "https://storage.googleapis.com/globetrotter-travel-media-qwiklabs-gcp-01-892a42380662/video_" in url
    assert url.endswith(".mp4")
    mock_tool_context.save_artifact.assert_called_once()
    mock_genai_client.assert_called_once_with(
        vertexai=True, project=PROJECT_ID, location="global"
    )
