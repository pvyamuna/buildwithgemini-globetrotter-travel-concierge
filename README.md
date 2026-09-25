# Globetrotter Travel Concierge

An intelligent AI Travel Concierge application built on Google Cloud's **Agent Development Kit (ADK)**, **Vertex AI Agent Runtime**, **A2UI**, **FastAPI**, **Firestore**, and **Cloud Storage**. Globetrotter assists travelers with discovering curated travel packages, generating visual destination preview photos and videos, converting currency rates, exploring nearby attractions, executing code calculations, and personalizing recommendations based on durable user memory preferences.

![Globetrotter Travel Concierge Demo](./docs/demo.gif)

---

## ⚙️ Environment Configuration (`dev` vs `live`)

Globetrotter maintains strict separation between **`dev`** (Sandbox & Local Testing) and **`live`** (Production Cloud Deployment):

| Configuration Variable | Development / Sandbox (`dev`) | Production / Deployed (`live`) |
| :--- | :--- | :--- |
| `APP_ENV` | `dev` | `live` |
| `GOOGLE_CLOUD_PROJECT` | Local Dev GCP Project ID | Production GCP Project ID |
| `GCS_BUCKET_NAME` | `globetrotter-travel-media-dev` | `globetrotter-travel-media-prod` |
| `MEMORY_BANK_ID` | Sandbox / Dev Memory Bank ID | Deployed Reasoning Engine ID |
| `AGENT_ENGINE_RESOURCE_NAME` | Local / Sandbox ADK Web URL | Deployed Vertex AI Reasoning Engine Resource Name |
| `USE_CODE_SANDBOX` | `true` | `true` |

### Environment Files
* `.env.dev`: Local sandbox development environment.
* `.env.prod`: Production live environment configuration.

To switch environments locally, set `APP_ENV`:
```bash
# Activate dev environment
export APP_ENV=dev

# Activate live environment
export APP_ENV=live
```

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

## 🔄 End-to-End Environment Lifecycle: Build, Test, Deploy

### 1. Build Phase
Build python wheel packages or container images for deployment:
```bash
# Build Python library wheel package
python -m pip install --upgrade build
python -m build

# Build Cloud Run frontend container locally (optional)
docker build -t globetrotter-frontend:latest -f frontend/Dockerfile .
```

### 2. Test Phase
Run unit tests, API contract tests, and integration tests across environments:
```bash
# Run unit and contract tests in dev environment
APP_ENV=dev ./.venv/bin/pytest tests/unit/ tests/contract/ -v

# Run integration tests against sandbox/agent
APP_ENV=dev ./.venv/bin/pytest tests/integration/ -v
```

### 3. Deploy Phase

#### A. Deploy Agent Runtime (`live`)
Deploy the ADK Agent to Vertex AI Reasoning Engine:
```bash
APP_ENV=live agents-cli deploy agent-engine \
  --project YOUR_PROJECT_ID \
  --region us-central1
```

#### B. Deploy Frontend to Cloud Run (`live`)
Deploy the FastAPI proxy server to Cloud Run:
```bash
gcloud run deploy globetrotter-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="APP_ENV=live,AGENT_ENGINE_RESOURCE_NAME=YOUR_REASONING_ENGINE_RESOURCE_NAME,AGENT_DIRECTORY=app"
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

## 🛠️ Project Structure

```
globetrotter-travel-concierge/
├── app/                        # Agent backend & library API package
│   ├── __init__.py             # Re-exports GlobetrotterClient and run_agent_query
│   ├── config.py               # Environment configuration loader (dev vs live)
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
├── .env.dev                    # Dev/Sandbox environment settings
├── .env.prod                   # Live/Production environment settings
├── BUILD_SIMILAR_AGENT.md      # Comprehensive guide & blueprint for building new ADK agents
├── agents-cli-manifest.yaml    # Deployment manifest
├── pyproject.toml              # Python build specification
└── README.md                   # Project documentation
```
