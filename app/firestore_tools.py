"""Firestore tools for Globetrotter Travel Concierge.

HARDCODED PROJECT ID: qwiklabs-gcp-01-892a42380662
Do not use google.auth.default() or GOOGLE_CLOUD_PROJECT env var.
"""

from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-01-892a42380662"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)


def search_travel_packages(destination: str = "", max_price: int = 0) -> str:
    """Searches travel packages from the Firestore database catalog.

    Args:
        destination: Optional destination filter string (e.g., 'Tokyo', 'Paris', 'Bali').
        max_price: Optional maximum price filter in USD (e.g. 2000). Set to 0 for no price limit.

    Returns:
        A string formatted list of matching travel packages from Firestore.
    """
    db = _get_firestore_client()
    collection_ref = db.collection("travel_packages")
    docs = collection_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        doc_dest = data.get("destination", "").lower()
        price = data.get("price_usd", 0)

        # Apply filters
        if destination and destination.lower() not in doc_dest:
            continue
        if max_price > 0 and price > max_price:
            continue

        results.append(data)

    if not results:
        return f"No travel packages found matching destination='{destination}' and max_price={max_price}."

    output_lines = [f"Found {len(results)} travel package(s):"]
    for pkg in results:
        output_lines.append(
            f"- [{pkg.get('id')}] {pkg.get('title')} ({pkg.get('destination')}): "
            f"${pkg.get('price_usd')} USD, {pkg.get('duration_days')} days. Vibe: {pkg.get('vibe')}. "
            f"Description: {pkg.get('description')}"
        )
    return "\n".join(output_lines)


def get_travel_package_details(package_id: str) -> str:
    """Retrieves full details for a specific travel package ID from Firestore.

    Args:
        package_id: The unique package ID (e.g. 'pkg_tokyo_01', 'pkg_paris_02').

    Returns:
        A string containing full details of the travel package.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("travel_packages").document(package_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Travel package with ID '{package_id}' not found in Firestore."

    data = doc.to_dict()
    highlights_str = ", ".join(data.get("highlights", []))
    return (
        f"Package Details for [{data.get('id')}]:\n"
        f"Title: {data.get('title')}\n"
        f"Destination: {data.get('destination')}\n"
        f"Duration: {data.get('duration_days')} Days\n"
        f"Price: ${data.get('price_usd')} USD\n"
        f"Vibe: {data.get('vibe')}\n"
        f"Highlights: {highlights_str}\n"
        f"Description: {data.get('description')}"
    )


def save_travel_package(
    package_id: str,
    destination: str,
    title: str,
    duration_days: int,
    price_usd: int,
    vibe: str,
    description: str,
    highlights: str = "",
) -> str:
    """Creates or updates a travel package document in the Firestore database catalog.

    Args:
        package_id: Unique package identifier (e.g., 'pkg_custom_05').
        destination: City and country (e.g. 'Rome, Italy').
        title: Short package title.
        duration_days: Number of days for the trip.
        price_usd: Package cost in USD.
        vibe: Style or atmosphere of the trip.
        description: Brief overview of the travel package.
        highlights: Comma-separated list of key attractions or activities.

    Returns:
        A success confirmation string.
    """
    db = _get_firestore_client()
    highlights_list = [h.strip() for h in highlights.split(",") if h.strip()]

    doc_data = {
        "id": package_id,
        "destination": destination,
        "title": title,
        "duration_days": duration_days,
        "price_usd": price_usd,
        "vibe": vibe,
        "description": description,
        "highlights": highlights_list,
    }

    doc_ref = db.collection("travel_packages").document(package_id)
    doc_ref.set(doc_data)

    return f"Successfully saved travel package '{package_id}' ({title}) to Firestore."
