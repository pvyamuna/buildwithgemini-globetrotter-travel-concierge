# How to Build, Test, and Deploy an AI Agent with Cloud Run Frontend

This guide provides a comprehensive step-by-step walkthrough to **build, test, deploy, and wire up** a production AI agent using **Google Agent Development Kit (ADK)**, **Vertex AI Agent Runtime**, and a **FastAPI Cloud Run frontend**.

---

## 🛠️ Architecture Overview

The system architecture consists of two decoupled services connected over Google's **A2A (Agent-to-Agent)** protocol:

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

## 📋 Step 1: Scaffold & Build the Agent

### 1. Scaffold Project
Create a new ADK project targeting Vertex AI Agent Runtime:

```bash
agents-cli scaffold create \
  --name my-similar-agent \
  --template adk \
  --deployment-target agent_runtime
```

### 2. Configure Agent & Tools (`app/agent.py`)
Register custom tools, Vertex AI Memory Bank, and A2UI schema manager:

```python
from google.adk import Agent, App
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import PreloadMemoryTool
from google.genai import types
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

# A2UI Card Schema Manager
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

# Memory Bank Service
def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project="YOUR_PROJECT_ID",
        location="us-central1",
        agent_engine_id="YOUR_MEMORY_BANK_ID",
    )

root_agent = Agent(
    name="root_agent",
    model=Gemini(model="gemini-flash-latest"),
    instruction=schema_manager.generate_system_prompt(...),
    tools=[
        search_catalog,
        generate_item_photo,
        generate_destination_video,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
)

app = App(root_agent=root_agent)
```

---

## 🧪 Step 2: Test the Agent Locally

### 1. Run Automated Unit & Integration Tests
Execute `pytest` to verify tool definitions, memory hooks, and agent callbacks:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/
```

### 2. Test Agent Locally via ADK Web UI
Launch local ADK web interface to interactively test tools and A2UI card rendering:

```bash
agents-cli dev web
```

---

## 🚀 Step 3: Deploy the Agent Runtime (`agents-cli deploy`)

### 1. Deploy Agent to Vertex AI Reasoning Engine
Publish the ADK agent to Vertex AI Agent Runtime:

```bash
agents-cli deploy agent-engine \
  --project YOUR_PROJECT_ID \
  --region us-central1
```

After deployment completes, note down the returned Reasoning Engine resource name:
`projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/YOUR_REASONING_ENGINE_ID`

### 2. Grant IAM Authorization
Grant the default Cloud Run Compute Service Account permission to invoke Vertex AI Reasoning Engines:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## 🌐 Step 4: Build & Deploy the Cloud Run Frontend

### 1. Pin Dependencies (`frontend/requirements.txt`)
Ensure `a2a-sdk` is pinned to `0.3.26` to avoid breaking changes during container builds:

```text
a2a-sdk==0.3.26
fastapi
uvicorn
google-auth
```

### 2. FastAPI A2A Proxy Server (`frontend/main.py`)
The proxy uses Google Application Default Credentials (ADC) to authenticate A2A requests:

```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import a2a.client

app = FastAPI()

AGENT_ENGINE_RESOURCE_NAME = os.environ.get("AGENT_ENGINE_RESOURCE_NAME")
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")

@app.post("/chat")
async def chat(request: dict):
    user_message = request.get("message")
    # Fetch agent card via A2A protocol and send user message
    # Return { "parts": [{ "kind": "text", "text": "..." }, { "kind": "a2ui", "data": [...] }] }
```

### 3. Deploy Frontend to Cloud Run
Deploy the FastAPI container to Cloud Run with environment variables pointing to your Agent Runtime ID:

```bash
gcloud run deploy my-agent-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/YOUR_REASONING_ENGINE_ID",AGENT_DIRECTORY="app"
```

---

## ✅ Step 5: End-to-End Verification

### 1. Endpoint HTTP Verification
Test the deployed Cloud Run service URL using `curl`:

```bash
# Verify chat POST endpoint
curl -X POST https://<YOUR_CLOUD_RUN_URL>/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, search travel packages for Tokyo"}'
```

### 2. Live Browser Verification
Open `https://<YOUR_CLOUD_RUN_URL>` in your browser to verify:
* **Prompt Chips**: Clickable prompt chips trigger instant queries.
* **Preferences Modal**: Displays durable memory facts retrieved from Vertex AI Memory Bank.
* **A2UI Cards**: Interactive cards render cleanly without raw JSON artifacts.
* **Media & Code Execution**: Generates photos/videos and performs live sandbox calculations.
