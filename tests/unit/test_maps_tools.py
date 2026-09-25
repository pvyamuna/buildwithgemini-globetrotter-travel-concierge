"""Unit tests for Geocoding and Places (New) tools."""

from unittest.mock import MagicMock, patch
from app.maps_tools import find_nearby_places, geocode_address


@patch("app.maps_tools.urllib.request.urlopen")
@patch("app.maps_tools._get_api_key", return_value="fake_maps_key")
def test_geocode_address_success(mock_key, mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"""{
        "status": "OK",
        "results": [
            {
                "formatted_address": "Shibuya Crossing, Tokyo, Japan",
                "geometry": {
                    "location": {"lat": 35.6595, "lng": 139.7004}
                }
            }
        ]
    }"""
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = geocode_address("Shibuya Crossing, Tokyo")
    assert "Geocoding Result for 'Shibuya Crossing, Tokyo'" in res
    assert "Shibuya Crossing, Tokyo, Japan" in res
    assert "Latitude: 35.6595, Longitude: 139.7004" in res


@patch("app.maps_tools.urllib.request.urlopen")
@patch("app.maps_tools._get_api_key", return_value="fake_maps_key")
def test_find_nearby_places_success(mock_key, mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"""{
        "places": [
            {
                "displayName": {"text": "Ichiran Ramen"},
                "formattedAddress": "1-22-7 Jinnan, Shibuya City, Tokyo",
                "location": {"latitude": 35.6610, "longitude": 139.7012}
            }
        ]
    }"""
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = find_nearby_places(latitude=35.6595, longitude=139.7004, place_type="restaurant")
    assert "Nearby 'restaurant' Places" in res
    assert "Ichiran Ramen" in res
    assert "1-22-7 Jinnan, Shibuya City, Tokyo" in res
    assert "(35.661, 139.7012)" in res
