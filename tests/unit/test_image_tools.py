"""Unit tests for image generation tools."""

from unittest.mock import MagicMock, patch
from app.image_tools import (
    generate_destination_image,
    generate_travel_item_image,
    GCS_BUCKET_NAME,
    PROJECT_ID,
)


def test_image_tools_config():
    assert PROJECT_ID == "qwiklabs-gcp-01-892a42380662"
    assert GCS_BUCKET_NAME == "globetrotter-travel-media-qwiklabs-gcp-01-892a42380662"


@patch("app.image_tools.storage.Client")
@patch("app.image_tools.genai.Client")
def test_generate_destination_image_success(mock_genai_client, mock_storage_client):
    mock_gcs = MagicMock()
    mock_storage_client.return_value = mock_gcs

    mock_ai = MagicMock()
    mock_genai_client.return_value = mock_ai
    mock_img = MagicMock()
    mock_img.image.image_bytes = b"fake_jpeg_bytes"
    mock_ai.models.generate_images.return_value.generated_images = [mock_img]

    url = generate_destination_image("Kyoto Bamboo Forest")
    assert "https://storage.googleapis.com/globetrotter-travel-media-qwiklabs-gcp-01-892a42380662/destination_" in url
    assert url.endswith(".jpg")


@patch("app.image_tools.storage.Client")
@patch("app.image_tools.genai.Client")
def test_generate_travel_item_image_success(mock_genai_client, mock_storage_client):
    mock_gcs = MagicMock()
    mock_storage_client.return_value = mock_gcs

    mock_ai = MagicMock()
    mock_genai_client.return_value = mock_ai

    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake_image_bytes"
    mock_part.inline_data.mime_type = "image/jpeg"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    mock_ai.models.generate_content.return_value.candidates = [mock_candidate]

    mock_tool_context = MagicMock()

    url = generate_travel_item_image("Luxury hotel suite in Paris", tool_context=mock_tool_context)
    assert "https://storage.googleapis.com/globetrotter-travel-media-qwiklabs-gcp-01-892a42380662/travel_" in url
    assert url.endswith(".jpg")
    mock_tool_context.save_artifact.assert_called_once()

