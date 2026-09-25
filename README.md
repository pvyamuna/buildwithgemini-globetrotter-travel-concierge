# Globetrotter Travel Concierge

An intelligent AI Travel Concierge application built on Google Cloud's **Agent Development Kit (ADK)**, **Vertex AI Agent Runtime**, **A2UI**, **FastAPI**, **Firestore**, and **Cloud Storage**. Globetrotter assists travelers with discovering curated travel packages, generating visual destination preview photos and videos, converting currency rates, exploring nearby attractions, executing code calculations, and personalizing recommendations based on durable user memory preferences.

![Globetrotter Travel Concierge Demo](./docs/demo.gif)

---

## 🏛️ System Architecture

Globetrotter connects a responsive web chat UI to a deployed ADK Agent Runtime over Google's A2A protocol, augmented with enterprise GCP data services and GenAI models:

```
┌─────────────────────────┐          HTTP POST /chat          ┌───────────────────────────┐
│   Web Browser Client    │ ─────────────────────────────────► │  Cloud Run Frontend Proxy │
│ (Prompt Chips & Modal)  │ ◄───────────────────────────────── │   (FastAPI + Swagger UI)  │
└─────────────────────────┘      JSON {parts:[text, a2ui]}    └─────────────┬─────────────┘
                                                                            │
                                                                 A2A Protocol / gRPC
                                                                            │
                                                                            ▼
                                                              ┌───────────────────────────┐
                                                              │ Vertex AI Agent Runtime   │
                                                              │ (ADK Agent + Reasoning)   │
                                                              └─────────────┬─────────────┘
                                                                            │
                                            ┌───────────────────────────────┼───────────────────────────────┐
                                            ▼                               ▼                               ▼
                                  ┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
                                  │ Vertex Memory Bank│           │ Firestore Catalog │           │ GCS Media Bucket  │
                                  └───────────────────┘           └───────────────────┘           └───────────────────┘
```

---

## 🐍 Public Python Library API (`app/api.py`)

Globetrotter can be imported and executed as a reusable Python library package in downstream applications:

```python
from app import GlobetrotterClient, run_agent_query

# 1. Quick Functional API
result = run_agent_query("Calculate 7-day budget in Tokyo in JPY and EUR")
print(result["text"])

# 2. Client Class API
client = GlobetrotterClient(user_id="my-app-user")

# Inspect registered agent tools
print(client.list_available_tools())
# -> ['get_weather', 'search_travel_packages', 'generate_destination_image', 'generate_destination_video', ...]

# Synchronous Query
res = client.query("Search travel packages for Bali beach getaway")
print(res["text"])
```

---

## 🌐 OpenAPI / Swagger Interactive Documentation

When running the frontend server or deployed on Cloud Run, interactive API documentation is available at:

* **Swagger UI**: `http://localhost:8080/docs` (or `https://<YOUR_CLOUD_RUN_URL>/docs`)
* **ReDoc**: `http://localhost:8080/redoc`

### API Endpoints
* `GET /health`: Health check endpoint for Cloud Run and uptime monitoring.
* `POST /chat`: Primary chat endpoint forwarding browser queries over A2A protocol to Agent Runtime.

---

## 🚀 Implemented Capabilities & Google Cloud Services

Globetrotter is wired to the following Google Cloud infrastructure and GenAI capabilities:

* **Vertex AI Memory Bank**: Durable cross-session user memory (`VertexAiMemoryBankService`, `PreloadMemoryTool`) storing traveler facts and preferences across independent conversation sessions.
* **Google Cloud Firestore**: NoSQL document database indexing travel package catalog records (`search_travel_packages`, `get_travel_package_details`, `save_travel_package`).
* **Google Cloud Storage (GCS)**: Public media bucket hosting generated destination photos, postcard graphics, and video previews.
* **Generative AI Models**:
  * `gemini-flash-latest`: Primary reasoning and tool-orchestration model.
  * `gemini-3.1-flash-lite-image`: Travel item and destination photo generation.
  * `imagen-3.0-generate-002`: High-fidelity destination preview graphics.
  * `gemini-omni-flash-preview` (*Global Region*): Short destination video generation.
* **A2UI (Agent-to-User Interface v0.8)**: Generates structured display UI cards (`Card`, `Column`, `Row`, `Text`, `Image`) rendered directly in the frontend chat surface.
* **Agent Engine Code Sandbox**: Secure container executor (`AgentEngineSandboxCodeExecutor`) for running Python calculations for trip budget totals and currency conversions.
* **Currency & Location Tools**: Live currency exchange rates (`get_currency_exchange_rates`), Google Maps geocoding (`geocode_address`), and place search (`find_nearby_places`).
* **Weather & Time Tools**: Weather forecast query lookup (`get_weather`) and time zone checks (`get_current_time`).

---

## 🛠️ Project Structure

```
globetrotter-travel-concierge/
├── app/                        # Agent backend & library API package
│   ├── __init__.py             # Re-exports GlobetrotterClient and run_agent_query
│   ├── agent.py                # ADK Agent definition, system instructions, and tool registry
│   ├── api.py                  # Public Python Library API client
│   ├── a2ui_utils.py           # A2UI callback and card generation utilities
│   ├── currency_tools.py       # Live currency exchange rate tool
│   ├── firestore_tools.py      # Firestore database travel package catalog tools
│   ├── image_tools.py          # Gemini & Imagen photo generation tools
│   ├── maps_tools.py           # Geocoding and Google Maps location tools
│   └── video_tools.py          # Gemini Omni video generation tool
├── frontend/                   # Web frontend proxy & chat UI
│   ├── main.py                 # FastAPI proxy converting browser calls to A2A protocol (+ Swagger UI)
│   ├── static/index.html       # Responsive dialogue UI with prompt chips and preferences modal
│   └── Dockerfile              # Cloud Run container build file
├── tests/                      # Comprehensive test suite
│   ├── unit/                   # Tool and Python library API unit tests
│   ├── contract/               # FastAPI & OpenAPI contract tests
│   └── integration/            # Agent integration tests
├── BUILD_SIMILAR_AGENT.md      # Comprehensive guide & blueprint for building new ADK agents
├── agents-cli-manifest.yaml    # Deployment manifest
├── pyproject.toml              # Python build specification
└── README.md                   # Project documentation
```

---

## 💻 Local Setup & Run Instructions

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Agent Locally
```bash
uv run adk web . --port 8080 --reload_agents
```

### 3. Run Frontend Server Locally
```bash
pip install -r frontend/requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/YOUR_ENGINE_ID"
python frontend/main.py
```

---

## 🧪 Running Tests

Execute the unit, contract, and integration test suites:

```bash
# Run unit and API contract tests
./.venv/bin/pytest tests/unit/ tests/contract/

# Run integration tests
./.venv/bin/pytest tests/integration/
```

---

## 📘 Building a New Similar Agent

To build your own AI agent from scratch using this codebase as a reference architecture, follow the step-by-step guide in **[BUILD_SIMILAR_AGENT.md](file:///config/Desktop/Session1/globetrotter-travel-concierge/BUILD_SIMILAR_AGENT.md)**.
