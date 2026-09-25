"""Maps Geocoding and Places (New) tools for Globetrotter Travel Concierge.

Reads GOOGLE_MAPS_API_KEY from environment variables (.env).
"""

import json
import os
import urllib.parse
import urllib.request
from dotenv import load_dotenv

load_dotenv()


def _get_api_key() -> str:
    return os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()


def geocode_address(address: str) -> str:
    """Converts an address or location name into geographic coordinates (latitude and longitude) using the Geocoding API.

    Args:
        address: The address or place name to geocode (e.g., 'Shibuya Crossing, Tokyo', 'Eiffel Tower, Paris').

    Returns:
        Formatted location details including address, latitude, and longitude.
    """
    api_key = _get_api_key()
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    req = urllib.request.Request(url, headers={"User-Agent": "Globetrotter-Travel-Agent/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            error_msg = data.get("error_message", f"Geocoding API status: {status}")
            return f"Could not geocode address '{address}': {error_msg}"

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address", address)
        location = first_result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"Geocoding Result for '{address}':\n"
            f"- Address: {formatted_address}\n"
            f"- Location: (Latitude: {lat}, Longitude: {lng})"
        )
    except Exception as e:
        return f"Failed to geocode address: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> str:
    """Finds nearby points of interest (restaurants, tourist attractions, hotels, etc.) near given coordinates using the Places API (New).

    Args:
        latitude: The latitude coordinate (e.g. 35.6762).
        longitude: The longitude coordinate (e.g. 139.6503).
        place_type: The place type category (e.g., 'restaurant', 'tourist_attraction', 'lodging', 'cafe', 'museum').
        radius_meters: Search radius in meters. Defaults to 1000.0.

    Returns:
        A formatted list of key fields (name, address, location coordinates) for nearby places.
    """
    api_key = _get_api_key()
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
        "User-Agent": "Globetrotter-Travel-Agent/1.0",
    }

    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        output = [f"Nearby '{place_type}' Places within {radius_meters}m:"]
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Name")
            address = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")

            output.append(
                f"- Name: {name}\n"
                f"  Address: {address}\n"
                f"  Location: ({lat}, {lng})"
            )

        return "\n".join(output)
    except Exception as e:
        return f"Failed to fetch nearby places: {str(e)}"
