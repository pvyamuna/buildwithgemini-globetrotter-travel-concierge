# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

import json
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback
from app.currency_tools import get_currency_exchange_rates
from app.firestore_tools import (
    get_travel_package_details,
    save_travel_package,
    search_travel_packages,
)
from app.image_tools import (
    generate_destination_image,
    generate_travel_item_image,
)
from app.maps_tools import find_nearby_places, geocode_address
from app.video_tools import generate_destination_video

PROJECT_ID = "952170692401"
MEMORY_BANK_ID = "7112427909024841728"


def memory_bank_service_builder():
    """Builds VertexAiMemoryBankService for deployed runtime."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-central1",
        agent_engine_id=MEMORY_BANK_ID,
    )


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract durable user memories across sessions in the background."""
    try:
        import asyncio
        asyncio.create_task(callback_context.add_session_to_memory())
    except Exception:
        pass
    return None


# Load Agent Engine / Sandbox resource name from deployment_metadata.json
DEPLOYMENT_METADATA_PATH = Path(__file__).parent.parent / "deployment_metadata.json"
sandbox_resource_name = None
agent_engine_resource_name = None

if DEPLOYMENT_METADATA_PATH.exists():
    try:
        meta = json.loads(DEPLOYMENT_METADATA_PATH.read_text())
        sandbox_resource_name = meta.get("sandbox_resource_name")
        agent_engine_resource_name = meta.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=sandbox_resource_name,
    agent_engine_resource_name=agent_engine_resource_name,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Globetrotter, an expert AI Travel & Itinerary Concierge. "
        "You help users explore travel packages stored in the Firestore database catalog, "
        "retrieve details for specific trips, save new packages, generate destination visual preview photos/postcards and travel item images, "
        "fetch live currency exchange rates, geocode addresses to coordinates, find nearby places (restaurants, attractions), "
        "check local weather, run calculations with code execution, and provide personalized trip recommendations. "
        "You remember the user's stated preferences and facts from previous conversations to personalize responses."
    ),
    workflow_description="Analyze the user request to discover travel destinations, search or save travel packages, generate destination photo previews, check weather, calculate trip costs, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=a2ui_instruction,
    tools=[
        get_weather,
        get_current_time,
        search_travel_packages,
        get_travel_package_details,
        save_travel_package,
        generate_destination_image,
        generate_travel_item_image,
        generate_destination_video,
        get_currency_exchange_rates,
        geocode_address,
        find_nearby_places,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

