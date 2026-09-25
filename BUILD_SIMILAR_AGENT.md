# How to Build a Similar AI Agent with Google ADK

This guide explains step-by-step how to build a production-grade AI agent similar to **Globetrotter Travel Concierge** using the **Google Agent Development Kit (ADK)**, **Vertex AI**, **Firestore**, **GCS**, **A2UI**, and **Cloud Run**.

---

## 🛠️ Architecture Overview

A complete ADK agent application consists of three main layers:

1. **ADK Agent Runtime**: The core Python agent defining system instructions, tools, Vertex AI Memory Bank integration, code execution sandbox, and A2UI card callbacks.
2. **FastAPI Proxy**: A lightweight server that connects web browsers to the agent's **A2A (Agent-to-Agent)** protocol endpoint on Vertex AI Reasoning Engine.
3. **Web Frontend**: A responsive HTML/CSS/JS chat interface rendering plain-text responses, prompt chips, dialogue modals, and A2UI cards.

---

## 📋 Step-by-Step Implementation Guide

### Step 1: Scaffold a New Agent Project
Initialize a fresh ADK agent project using `agents-cli`:

```bash
agents-cli scaffold create \
  --name my-similar-agent \
  --template adk \
  --deployment-target agent_runtime
```

---

### Step 2: Define Custom Tools & Integrations

#### 1. Firestore Database Catalog Tools
Create tools for searching or persisting data in Cloud Firestore (`app/firestore_tools.py`):

```python
from google.cloud import firestore

db = firestore.Client(project="YOUR_PROJECT_ID")

def search_catalog(query: str) -> list[dict]:
    """Searches catalog items in Firestore.
    
    Args:
        query: Search term or keyword.
    """
    docs = db.collection("items").limit(5).stream()
    return [doc.to_dict() for doc in docs]
```

#### 2. Generative Media Tools (Imagen & Gemini Omni Video)
Create visual tools that generate images or short video clips and upload bytes to Cloud Storage (`app/media_tools.py`):

```python
import uuid
from google import genai
from google.cloud import storage

def generate_item_photo(prompt: str) -> str:
    """Generates a photo for an item and uploads it to Cloud Storage."""
    client = genai.Client(vertexai=True, project="YOUR_PROJECT_ID", location="us-central1")
    res = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=dict(number_of_images=1, output_mime_type="image/jpeg"),
    )
    image_bytes = res.generated_images[0].image.image_bytes
    
    # Upload bytes to Cloud Storage
    filename = f"media_{uuid.uuid4().hex[:8]}.jpg"
    storage_client = storage.Client(project="YOUR_PROJECT_ID")
    blob = storage_client.bucket("YOUR_BUCKET_NAME").blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    
    return f"https://storage.googleapis.com/YOUR_BUCKET_NAME/{filename}"
```

#### 3. Vertex AI Memory Bank Integration
Enable cross-session memory in `app/agent.py`:

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import PreloadMemoryTool

def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project="YOUR_PROJECT_ID",
        location="us-central1",
        agent_engine_id="YOUR_MEMORY_BANK_ID",
    )
```

---

### Step 3: Wire the Agent with A2UI Card Callbacks
Register tools, Memory Bank, and A2UI schema manager in `app/agent.py`:

```python
from google.adk import Agent, App
from google.genai import types
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(model="gemini-flash-latest"),
    instruction=schema_manager.generate_system_prompt(...),
    tools=[
        search_catalog,
        generate_item_photo,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
)

app = App(root_agent=root_agent)
```

---

### Step 4: Build & Deploy the FastAPI Proxy Frontend
The FastAPI proxy translates browser `/chat` requests into A2A protocol calls to Agent Runtime:

```python
# frontend/main.py
from fastapi import FastAPI
import a2a.client

app = FastAPI()
# Sends user message to agent A2A endpoint and returns text & A2UI dataparts
```

Deploy frontend to Cloud Run:

```bash
gcloud run deploy my-agent-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="YOUR_AGENT_RESOURCE_NAME",AGENT_DIRECTORY="app"
```

---

## 🧪 Testing Your Agent
Run automated pytest verification:

```bash
pytest tests/unit/
```
