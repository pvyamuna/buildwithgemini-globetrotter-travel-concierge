"""Unit tests for Firestore tools."""

from unittest.mock import MagicMock, patch
from app.firestore_tools import (
    FIRESTORE_PROJECT,
    get_travel_package_details,
    save_travel_package,
    search_travel_packages,
)


def test_firestore_project_id_hardcoded():
    assert FIRESTORE_PROJECT == "qwiklabs-gcp-01-892a42380662"


@patch("app.firestore_tools._get_firestore_client")
def test_search_travel_packages_with_filter(mock_get_client):
    mock_db = MagicMock()
    mock_get_client.return_value = mock_db

    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        "id": "pkg_tokyo_01",
        "destination": "Tokyo, Japan",
        "title": "Tokyo Neon Explorer",
        "duration_days": 5,
        "price_usd": 1850,
        "vibe": "Culture & Tech",
        "description": "Fun in Tokyo",
    }

    mock_doc2 = MagicMock()
    mock_doc2.to_dict.return_value = {
        "id": "pkg_paris_02",
        "destination": "Paris, France",
        "title": "Paris Romance",
        "duration_days": 6,
        "price_usd": 2400,
        "vibe": "Romance",
        "description": "Fun in Paris",
    }

    mock_db.collection().stream.return_value = [mock_doc1, mock_doc2]

    res = search_travel_packages(destination="Tokyo")
    assert "Tokyo Neon Explorer" in res
    assert "Paris Romance" not in res


@patch("app.firestore_tools._get_firestore_client")
def test_get_travel_package_details(mock_get_client):
    mock_db = MagicMock()
    mock_get_client.return_value = mock_db

    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "id": "pkg_tokyo_01",
        "destination": "Tokyo, Japan",
        "title": "Tokyo Neon Explorer",
        "duration_days": 5,
        "price_usd": 1850,
        "vibe": "Culture & Tech",
        "highlights": ["Shibuya", "Akihabara"],
        "description": "Fun in Tokyo",
    }
    mock_db.collection().document().get.return_value = mock_doc

    res = get_travel_package_details("pkg_tokyo_01")
    assert "Tokyo Neon Explorer" in res
    assert "Shibuya" in res


@patch("app.firestore_tools._get_firestore_client")
def test_save_travel_package(mock_get_client):
    mock_db = MagicMock()
    mock_get_client.return_value = mock_db

    res = save_travel_package(
        package_id="pkg_test_99",
        destination="Rome, Italy",
        title="Roman Holiday",
        duration_days=4,
        price_usd=1600,
        vibe="History & Food",
        description="Explore ancient Rome",
        highlights="Colosseum, Vatican",
    )

    assert "Successfully saved travel package" in res
    mock_db.collection().document().set.assert_called_once_with(
        {
            "id": "pkg_test_99",
            "destination": "Rome, Italy",
            "title": "Roman Holiday",
            "duration_days": 4,
            "price_usd": 1600,
            "vibe": "History & Food",
            "description": "Explore ancient Rome",
            "highlights": ["Colosseum", "Vatican"],
        }
    )
