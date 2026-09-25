import os
from unittest.mock import patch
from app.config import load_config


def test_load_config_dev():
    with patch.dict(os.environ, {"APP_ENV": "dev", "GOOGLE_CLOUD_PROJECT": "test-project-dev"}):
        cfg = load_config()
        assert cfg.env == "dev"
        assert cfg.project_id == "test-project-dev"


def test_load_config_live():
    with patch.dict(os.environ, {"APP_ENV": "live", "GOOGLE_CLOUD_PROJECT": "test-project-prod"}):
        cfg = load_config()
        assert cfg.env == "live"
        assert cfg.project_id == "test-project-prod"
