"""Configuration module supporting separate 'dev' (Sandbox/Local) and 'live' (Production) environments."""

import os
from pathlib import Path
from typing import NamedTuple


class AppConfig(NamedTuple):
    env: str
    project_id: str
    location: str
    gcs_bucket: str
    memory_bank_id: str
    agent_engine_resource_name: str
    google_maps_api_key: str
    use_sandbox: bool


def load_config() -> AppConfig:
    """Loads configuration based on APP_ENV ('dev' or 'live').

    Defaults to 'dev' when running locally.
    """
    app_env = os.environ.get("APP_ENV", "dev").lower()
    
    # Try loading environment file if exists
    env_file_name = ".env.prod" if app_env in ("live", "prod", "production") else ".env.dev"
    env_path = Path(__file__).parent.parent / env_file_name
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"

    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())
        except Exception:
            pass

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "952170692401")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    default_bucket = (
        f"globetrotter-travel-media-{project_id}-live"
        if app_env in ("live", "prod", "production")
        else f"globetrotter-travel-media-{project_id}"
    )
    gcs_bucket = os.environ.get("GCS_BUCKET_NAME", default_bucket)
    memory_bank_id = os.environ.get("MEMORY_BANK_ID", "7112427909024841728")
    agent_engine_resource_name = os.environ.get(
        "AGENT_ENGINE_RESOURCE_NAME",
        f"projects/{project_id}/locations/{location}/reasoningEngines/7112427909024841728"
    )
    google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    use_sandbox = os.environ.get("USE_CODE_SANDBOX", "true").lower() in ("true", "1", "yes")

    return AppConfig(
        env=app_env,
        project_id=project_id,
        location=location,
        gcs_bucket=gcs_bucket,
        memory_bank_id=memory_bank_id,
        agent_engine_resource_name=agent_engine_resource_name,
        google_maps_api_key=google_maps_api_key,
        use_sandbox=use_sandbox,
    )


# Active runtime configuration
config = load_config()
