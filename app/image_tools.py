"""Image generation tools for Globetrotter Travel Concierge.

HARDCODED PROJECT ID: qwiklabs-gcp-01-892a42380662
HARDCODED BUCKET NAME: globetrotter-travel-media-qwiklabs-gcp-01-892a42380662
"""

import io
import uuid
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types
from PIL import Image, ImageDraw

PROJECT_ID = "qwiklabs-gcp-01-892a42380662"
GCS_BUCKET_NAME = "globetrotter-travel-media-qwiklabs-gcp-01-892a42380662"


def generate_travel_item_image(
    prompt: str, tool_context: ToolContext = None
) -> str:
    """Generates an image for a travel item or destination using the gemini-3.1-flash-lite-image model, saves it to the session artifacts, and uploads it to public Cloud Storage.

    Args:
        prompt: Detailed description of the travel item or location (e.g., 'Overwater bungalow in Bora Bora at sunset', 'Traditional Japanese bento box meal').
        tool_context: ADK ToolContext injected automatically for session artifact saving.

    Returns:
        The public HTTPS URL of the uploaded image on Cloud Storage.
    """
    filename = f"travel_{uuid.uuid4().hex[:8]}.jpg"

    # Call gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    part = res.candidates[0].content.parts[0]
    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/jpeg"

    # 1. Save artifact with tool_context for ADK Web Playground
    if tool_context:
        tool_context.save_artifact(
            filename=filename,
            artifact=types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        )

    # 2. Upload image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"


def generate_destination_image(prompt: str) -> str:
    """Generates a destination preview photo or postcard graphic and uploads it to public Cloud Storage.

    Args:
        prompt: A descriptive prompt for the destination image (e.g., 'Sunset over Shibuya Crossing in Tokyo').

    Returns:
        The public HTTPS URL of the generated image.
    """
    filename = f"destination_{uuid.uuid4().hex[:8]}.jpg"
    image_bytes = None

    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
        res = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=dict(number_of_images=1, output_mime_type="image/jpeg"),
        )
        if res.generated_images:
            image_bytes = res.generated_images[0].image.image_bytes
    except Exception:
        image_bytes = None

    if not image_bytes:
        img = Image.new("RGB", (800, 500), color="#1E1E2E")
        draw = ImageDraw.Draw(img)

        for y in range(300):
            r = int(255 - (y * 0.4))
            g = int(120 + (y * 0.3))
            b = int(180 + (y * 0.2))
            draw.line([(0, y), (800, y)], fill=(r, g, b))

        draw.ellipse([350, 160, 450, 260], fill="#F9E2AF")
        draw.rectangle([0, 300, 800, 500], fill="#11111B")

        clean_title = prompt.strip().upper()[:35]
        draw.text((40, 350), f"POSTCARD FROM {clean_title}", fill="#CDD6F4")
        draw.text((40, 400), "Globetrotter Travel Concierge", fill="#A6E3A1")

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        image_bytes = buf.getvalue()

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
