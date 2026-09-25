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

## ⚙️ 1. Configuration System (`app/config.py`)

Globetrotter maintains strict separation between **`dev`** (Sandbox & Local Testing) and **`live`** (Production Cloud Deployment):

| Configuration Variable | Development / Sandbox (`dev`) | Production / Deployed (`live`) |
| :--- | :--- | :--- |
| `APP_ENV` | `dev` | `live` |
| `GOOGLE_CLOUD_PROJECT` | Local Dev GCP Project ID | Production GCP Project ID |
| `GCS_BUCKET_NAME` | `globetrotter-travel-media-dev` | `globetrotter-travel-media-prod` |
| `MEMORY_BANK_ID` | Sandbox / Dev Memory Bank ID | Deployed Reasoning Engine ID |
| `AGENT_ENGINE_RESOURCE_NAME` | Local / Sandbox ADK Web URL | Deployed Vertex AI Reasoning Engine Resource Name |
| `USE_CODE_SANDBOX` | `true` | `true` |

### Environment Configuration Files
* **`.env.dev`**: Local sandbox development configuration.
* **`.env.prod`**: Production live configuration.

To switch environment profiles locally:
```bash
# Activate dev environment
export APP_ENV=dev

# Activate live environment
export APP_ENV=live
```

---

## 🎨 2. Frontend Component (`frontend/`)

The web frontend consists of a lightweight, containerized FastAPI server and a sleek, responsive dialogue interface:

* **File Surface**: `frontend/main.py` & `frontend/static/index.html`
* **Features**:
  * **Interactive Prompt Chips**: 3 pre-configured prompt chips (`🌴 Search packages for Tokyo & Bali`, `📸 Preview photos for beach getaway`, `🧮 Calculate 7-day budget in EUR & JPY`).
  * **Traveler Preferences Modal**: Custom modal overlay allowing users to configure budget tiers, travel styles, and dietary needs.
  * **Native A2UI Renderer**: Built-in client-side renderer that transforms A2UI JSON output (`Card`, `Column`, `Row`, `Text`, `Image`) into native HTML display cards.

---

## 🤖 3. ADK Agent Component (`app/agent.py`)

The agent backend uses Google ADK and coordinates multiple GenAI models and enterprise tools:

* **Root Agent**: `root_agent` powered by `gemini-flash-latest`.
* **Integrated Tools**:
  * `search_travel_packages`, `get_travel_package_details`, `save_travel_package`: Firestore NoSQL database travel package catalog queries.
  * `generate_destination_image`, `generate_travel_item_image`: Image generation via `gemini-3.1-flash-lite-image` and `imagen-3.0-generate-002`.
  * `generate_destination_video`: Short destination video generation using Google's Omni model (`gemini-omni-flash-preview`) in region `global`.
  * `get_currency_exchange_rates`: Real-time foreign exchange rate lookup.
  * `geocode_address`, `find_nearby_places`: Google Maps geocoding and place discovery tools.
  * `PreloadMemoryTool`: Vertex AI Memory Bank integration for durable cross-session user memory.
  * `AgentEngineSandboxCodeExecutor`: Secure Python code sandbox for running calculations.

---

## 🐍 4. Public Python Library & API Component (`app/api.py`)

Globetrotter exports a public Python library SDK and exposes interactive Swagger/OpenAPI documentation:

### Python Library SDK Usage
```python
from app import GlobetrotterClient, run_agent_query

# 1. Quick Functional API
result = run_agent_query("Calculate 7-day budget in Tokyo in JPY and EUR")
print(result["text"])

# 2. Client Class API
client = GlobetrotterClient(user_id="my-app-user")

# Inspect registered agent tools
print(client.list_available_tools())

# Synchronous Query
res = client.query("Search travel packages for Bali beach getaway")
print(res["text"])
```

### Interactive OpenAPI / Swagger Documentation
When the server is running, access Swagger UI and ReDoc:
* **Swagger UI**: `http://localhost:8080/docs`
* **ReDoc**: `http://localhost:8080/redoc`

#### Endpoints
* `GET /health`: Health check endpoint for Cloud Run container monitoring.
* `POST /chat`: Primary A2A protocol endpoint forwarding queries to Agent Runtime.

---

## ☁️ 5. Cloud Run Container Deployment

The frontend proxy is containerized and deployed to Google Cloud Run:

### Dockerfile (`frontend/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/ .
ENV PORT=8080
EXPOSE 8080
CMD ["python", "main.py"]
```

### IAM Permissions & Deployment Commands

```bash
# 1. Grant Cloud Run Compute SA permissions to invoke Vertex AI Agent Runtime
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 2. Deploy Frontend to Cloud Run
gcloud run deploy globetrotter-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="APP_ENV=live,AGENT_ENGINE_RESOURCE_NAME=YOUR_REASONING_ENGINE_RESOURCE_NAME,AGENT_DIRECTORY=app"
```

---

## 🔄 Lifecycle: Build, Test, Deploy

### 1. Build
```bash
python -m build
```

### 2. Test
```bash
./.venv/bin/pytest tests/unit/ tests/contract/ -v
```

### 3. Deploy
```bash
# Deploy Agent to Agent Platform
APP_ENV=live agents-cli deploy agent-engine --project YOUR_PROJECT_ID --region us-central1

# Deploy Frontend to Cloud Run
gcloud run deploy globetrotter-frontend --source ./frontend --region us-central1
```

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
│   ├── unit/                   # Tool, config, and API unit tests
│   ├── contract/               # FastAPI & OpenAPI contract tests
│   └── integration/            # Agent integration tests
├── .env.dev                    # Dev/Sandbox environment settings
├── .env.prod                   # Live/Production environment settings
├── BUILD_SIMILAR_AGENT.md      # Comprehensive guide & blueprint for building new ADK agents
├── agents-cli-manifest.yaml    # Deployment manifest
├── pyproject.toml              # Python build specification
└── README.md                   # Project documentation
```
