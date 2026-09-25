# Build with Gemini · Track 3 — Complete Agent & Application Development Guide

In this guide, you'll learn how to build a complete, production-grade agentic application (**Globetrotter Travel Concierge**) using **Google Agent Development Kit (ADK)**, **Vertex AI Agent Runtime**, **Firestore**, **Cloud Storage**, **Vertex AI Memory Bank**, **Agent Engine Code Sandbox**, **A2UI**, and **Cloud Run**.

---

## 🧭 Overview & Lab Architecture

```
┌─────────────────────────┐          HTTP POST /chat          ┌───────────────────────────┐
│   Web Browser Client    │ ─────────────────────────────────► │  Cloud Run Frontend Proxy │
│ (Prompt Chips & Modal)  │ ◄───────────────────────────────── │   (FastAPI + A2A SDK)     │
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

## 1. Environment Setup

### Starter Repo & Skills
Setup workspace dependencies, **skills**, and **MCP servers**:
* **Developer Knowledge MCP**: Grounded access to official Google Cloud, ADK, and Firebase documentation.
* **Firebase MCP**: Live interaction with Firestore database collections.

---

## 2. Build Your First Agent

Scaffold a complete ADK project targeting Vertex AI Agent Runtime using `agents-cli`:

```bash
agents-cli scaffold create \
  --name globetrotter-travel-concierge \
  --template adk \
  --deployment-target agent_runtime
```

### Local Testing in ADK Playground
Launch local ADK dev UI with session tracing:

```bash
agents-cli dev web
```

---

## 3. Initial Deployment to Agent Platform

Deploy the scaffolded agent to Vertex AI Reasoning Engine:

```bash
agents-cli deploy agent-engine \
  --project YOUR_PROJECT_ID \
  --region us-central1
```

Save the generated Reasoning Engine resource name from `deployment_metadata.json`:
`projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/YOUR_REASONING_ENGINE_ID`

---

## 4. Add Persistent Storage

### Firestore Database
Store structured domain records (e.g. travel catalog packages) in Cloud Firestore (`app/firestore_tools.py`):

```python
from google.cloud import firestore

# Note: Hardcode project ID string for Firestore client on Agent Platform
db = firestore.Client(project="YOUR_PROJECT_ID")

def search_travel_packages(destination: str) -> list[dict]:
    """Searches travel packages in Firestore matching a destination keyword."""
    docs = db.collection("travel_packages").limit(5).stream()
    return [d.to_dict() for d in docs if destination.lower() in str(d.to_dict()).lower()]
```

### Cloud Storage (GCS)
Create a public GCS bucket for hosting generated media (photos, postcard graphics, videos):

```bash
gcloud storage buckets create gs://globetrotter-travel-media-YOUR_PROJECT_ID \
  --location=us-central1
```

---

## 5. Add Tools & Call External APIs

### Function Tools
Add deterministic tools for currency conversions, geocoding, and local place searches:

* **Live Exchange Rates**: Fetch real-time FX rates from `frankfurter.dev`.
* **Google Maps Platform**: Geocode addresses via Geocoding API and find nearby attractions via Places API (New).

---

## 6. Generative Media Tools

### Image Generation (`imagen-3.0-generate-002` / `gemini-3.1-flash-lite-image`)
Generate destination images, save artifacts for Playground inspection, and upload bytes to Cloud Storage (`app/image_tools.py`):

```python
import uuid
from google import genai
from google.cloud import storage

def generate_destination_image(prompt: str, tool_context=None) -> str:
    """Generates a destination preview photo and uploads it to Cloud Storage."""
    client = genai.Client(vertexai=True, project="YOUR_PROJECT_ID", location="us-central1")
    res = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=dict(number_of_images=1, output_mime_type="image/jpeg"),
    )
    image_bytes = res.generated_images[0].image.image_bytes

    # Save artifact for ADK Playground
    if tool_context and hasattr(tool_context, "save_artifact"):
        tool_context.save_artifact(filename="preview.jpg", artifact=types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

    # Upload to Cloud Storage
    filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
    blob = storage.Client(project="YOUR_PROJECT_ID").bucket("YOUR_BUCKET_NAME").blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    return f"https://storage.googleapis.com/YOUR_BUCKET_NAME/{filename}"
```

### Video Generation with Omni (`gemini-omni-flash-preview`)
Generate video clips using Google's Omni model in region `global` (`app/video_tools.py`):

```python
def generate_destination_video(prompt: str, tool_context=None) -> str:
    """Generates a short video clip using gemini-omni-flash-preview in global region."""
    client = genai.Client(vertexai=True, project="YOUR_PROJECT_ID", location="global")
    res = client.interactions.create(model="gemini-omni-flash-preview", input=prompt)
    video_bytes = res.output_video.data

    # Upload bytes to Cloud Storage and return public HTTPS URL
    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
    blob = storage.Client(project="YOUR_PROJECT_ID").bucket("YOUR_BUCKET_NAME").blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    return f"https://storage.googleapis.com/YOUR_BUCKET_NAME/{filename}"
```

---

## 7. Run Code in a Sandbox

Enable secure Python code execution on Agent Platform (`app/agent.py`):

```python
from google.adk.code_executor import AgentEngineSandboxCodeExecutor

code_executor = AgentEngineSandboxCodeExecutor(
    project="YOUR_PROJECT_ID",
    location="us-central1",
    agent_engine_id="YOUR_AGENT_ENGINE_ID",
)
```

---

## 8. Cross-Session Memory (Vertex AI Memory Bank)

Enable durable memory storing user facts across conversations:

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import PreloadMemoryTool

def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project="YOUR_PROJECT_ID",
        location="us-central1",
        agent_engine_id="YOUR_AGENT_ENGINE_ID",
    )
```

Start local dev UI with memory service connection:

```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://YOUR_AGENT_ENGINE_ID
```

---

## 9. Enrich Responses with A2UI

Wire A2UI v0.8 Schema Manager and `a2ui_callback` in `app/agent.py`:

```python
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(model="gemini-flash-latest"),
    instruction=schema_manager.generate_system_prompt(...),
    tools=[...],
    after_model_callback=a2ui_callback,
)
```

---

## 10. Build & Deploy Cloud Run Frontend

### 1. Pin Dependencies (`frontend/requirements.txt`)
```text
a2a-sdk==0.3.26
fastapi
uvicorn
google-auth
```

### 2. Redeploy Finished Agent & Grant Service Account Roles
```bash
# Redeploy agent to Agent Platform
agents-cli deploy agent-engine --project YOUR_PROJECT_ID --region us-central1

# Grant datastore and storage roles to agent runtime service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_AGENT_RUNTIME_SA@developer.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_AGENT_RUNTIME_SA@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### 3. Deploy Frontend to Cloud Run & Grant IAM Access
```bash
# Grant Cloud Run Compute SA permission to access Reasoning Engine
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Deploy Cloud Run frontend service
gcloud run deploy globetrotter-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="AGENT_ENGINE_RESOURCE_NAME=YOUR_REASONING_ENGINE_RESOURCE_NAME,AGENT_DIRECTORY=app"
```

---

## 11. Record Demo & Publish to GitHub

### Record Browser Demo Video
Use Playwright to capture a 2-3 turn demo video in WebM format, then convert to an optimized looping GIF:

```bash
ffmpeg -i demo.webm -vf "fps=12,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" docs/demo.gif
```

### Publish to Personal GitHub Account
Sign in via GitHub CLI device code flow, commit project files, and push to a public repository:

```bash
bash .agents/skills/publish-to-github/publish.sh prep
gh auth login --hostname github.com --git-protocol https --web
bash .agents/skills/publish-to-github/publish.sh commit
gh repo create buildwithgemini-globetrotter-travel-concierge --public --source=. --remote=origin --push
```
