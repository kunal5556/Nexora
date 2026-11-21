import os

os.environ["LLM_API_KEYS"] = "test-key-one,test-key-two"
os.environ["LLM_MODEL"] = "gemini/gemini-2.5-flash-lite"
os.environ["DATABASE_URL"] = "sqlite:///./test-placeholder.db"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["ENABLE_FAILURE_SIMULATION"] = "true"
os.environ["DEFAULT_SYSTEM_PROMPT"] = "You are a test assistant."
os.environ["CACHE_TTL_SECONDS"] = "3600"
os.environ["LLM_TIMEOUT_SECONDS"] = "5"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client
