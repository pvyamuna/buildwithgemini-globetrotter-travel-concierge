# Globetrotter Travel Concierge

An intelligent AI Travel Concierge application built on Google Cloud's **Agent Development Kit (ADK)** and **Vertex AI**. Globetrotter assists travelers with discovering curated travel packages, generating visual destination preview photos and videos, converting currency rates, exploring nearby attractions, and personalizing recommendations based on durable user memory preferences.

![Globetrotter Travel Concierge Demo](./docs/demo.gif)

---

## 🚀 Implemented Architecture & Google Cloud Services

Globetrotter is wired directly to the following Google Cloud infrastructure and GenAI capabilities:

* **Vertex AI Memory Bank**: Durable cross-session user memory (`VertexAiMemoryBankService`, `PreloadMemoryTool`) storing traveler facts and preferences (budget tier, travel style, preferred climate, dietary preferences) across independent conversation sessions.
* **Google Cloud Firestore**: NoSQL document database indexing travel packages (`search_travel_packages`, `get_travel_package_details`, `save_travel_package`).
* **Google Cloud Storage (GCS)**: Media bucket hosting generated destination photos, postcard graphics, and video previews.
* **Generative AI Models**:
  * `gemini-flash-latest`: Primary reasoning and tool-orchestration model.
  * `gemini-3.1-flash-lite-image`: Travel item and destination photo generation.
  * `imagen-3.0-generate-002`: High-fidelity destination preview graphics.
  * `gemini-omni-flash-preview` (*Global Region*): Short destination video generation.
* **A2UI (Agent-to-User Interface v0.8)**: Generates structured display UI cards (`Card`, `Column`, `Row`, `Text`, `Image`) rendered directly in the frontend chat surface.
* **Agent Engine Code Sandbox**: Secure container executor (`AgentEngineSandboxCodeExecutor`) for running Python calculations for trip budget totals and currency conversions.
* **Currency & Location Tools**: Live currency exchange rates, Google Maps geocoding (`geocode_address`), and place search (`find_nearby_places`).
* **Weather & Time Tools**: Weather forecast query lookup (`get_weather`) and time zone checks (`get_current_time`).

---

## 🛠️ Project Structure

```
globetrotter-travel-concierge/
├── app/                        # Agent backend module
│   ├── agent.py                # ADK Agent definition, system instructions, and tool registry
│   ├── a2ui_utils.py           # A2UI callback and card generation utilities
│   ├── currency_tools.py       # Live currency exchange rate tool
│   ├── firestore_tools.py      # Firestore database travel package catalog tools
│   ├── image_tools.py          # Gemini & Imagen photo generation tools
│   ├── maps_tools.py           # Geocoding and Google Maps location tools
│   ├── video_tools.py          # Gemini Omni video generation tool
│   └── fast_api_app.py         # FastAPI agent endpoint
├── frontend/                   # Web frontend proxy & chat UI
│   ├── main.py                 # FastAPI proxy converting browser calls to A2A protocol
│   ├── static/index.html       # Responsive dialogue UI with prompt chips and preferences modal
│   └── Dockerfile              # Cloud Run container build file
├── tests/                      # Test suite
│   ├── unit/                   # Tool unit tests
│   └── integration/            # Agent integration tests
├── agents-cli-manifest.yaml    # Deployment manifest
└── README.md                   # Project documentation
```

---

## 💻 Local Setup & Development Instructions

### 1. Environment Requirements
* Python 3.11+
* Google Cloud SDK (`gcloud` CLI) authenticated with access to Vertex AI, Firestore, and GCS.

### 2. Install Dependencies
Set up a Python virtual environment and install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Environment Variables
Set your Google Cloud project configuration:

```bash
export GOOGLE_CLOUD_PROJECT="<YOUR_GCP_PROJECT_ID>"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_ENTERPRISE=True
```

### 4. Run the Agent Locally
Start the ADK development web UI:

```bash
agents-cli dev web
```

Or run the agent server directly with ADK:

```bash
adk web app
```

### 5. Run the FastAPI Frontend Proxy Locally
In a separate terminal, navigate to the frontend directory and start Uvicorn:

```bash
pip install -r frontend/requirements.txt
uvicorn frontend.main:app --host 0.0.0.0 --port 8080
```

---

## 🧪 Running Tests

Execute the unit and integration test suite with `pytest`:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```
