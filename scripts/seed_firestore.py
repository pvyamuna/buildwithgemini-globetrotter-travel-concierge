#!/usr/bin/env python3
"""Seed script for Firestore travel packages database.

HARDCODED PROJECT ID: qwiklabs-gcp-01-892a42380662
Do not use google.auth.default() or GOOGLE_CLOUD_PROJECT env var.
"""

from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-01-892a42380662"

SEED_PACKAGES = [
    {
        "id": "pkg_tokyo_01",
        "destination": "Tokyo, Japan",
        "title": "Tokyo Neon & Heritage Explorer",
        "duration_days": 5,
        "price_usd": 1850,
        "vibe": "Culture & Technology",
        "highlights": [
            "Shibuya Crossing",
            "Senso-ji Temple",
            "Akihabara Tech Tour",
            "Mount Fuji Day Trip",
        ],
        "description": "Experience the perfect fusion of ancient tradition and futuristic innovation in Tokyo.",
    },
    {
        "id": "pkg_paris_02",
        "destination": "Paris, France",
        "title": "Parisian Romance & Culinary Delights",
        "duration_days": 6,
        "price_usd": 2400,
        "vibe": "Romance & Cuisine",
        "highlights": [
            "Eiffel Tower Sunset",
            "Louvre Guided Tour",
            "Le Marais Bakery Crawl",
            "Versailles Palace",
        ],
        "description": "Stroll through historic boulevards, savor world-class dining, and admire legendary art.",
    },
    {
        "id": "pkg_bali_03",
        "destination": "Bali, Indonesia",
        "title": "Bali Tropical Wellness & Temple Sanctuary",
        "duration_days": 7,
        "price_usd": 1450,
        "vibe": "Wellness & Nature",
        "highlights": [
            "Ubud Monkey Forest",
            "Tegallalang Rice Terraces",
            "Sacred Water Temple Blessing",
            "Canggu Sunset Beach",
        ],
        "description": "Recharge in lush tropical rainforests, pristine beaches, and serene spiritual temples.",
    },
    {
        "id": "pkg_reykjavik_04",
        "destination": "Reykjavik, Iceland",
        "title": "Icelandic Northern Lights & Geothermal Wonders",
        "duration_days": 4,
        "price_usd": 2100,
        "vibe": "Adventure & Nature",
        "highlights": [
            "Golden Circle Tour",
            "Blue Lagoon Spa",
            "Northern Lights Hunt",
            "Black Sand Beach",
        ],
        "description": "Marvel at geysers, majestic waterfalls, volcanic landscapes, and aurora borealis views.",
    },
]


def seed_database():
    print(f"Connecting to Firestore with project ID: {FIRESTORE_PROJECT}...")
    db = firestore.Client(project=FIRESTORE_PROJECT)
    collection_ref = db.collection("travel_packages")

    for item in SEED_PACKAGES:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"  ✓ Seeded package '{item['id']}': {item['title']}")

    print("Firestore database seeded successfully!")


if __name__ == "__main__":
    seed_database()
