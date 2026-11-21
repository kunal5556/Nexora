import os

os.environ["LLM_API_KEYS"] = "test-key-one,test-key-two"
os.environ["LLM_MODEL"] = "gemini/gemini-3.5-flash-lite"
os.environ["DATABASE_URL"] = "sqlite:///./test-placeholder.db"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["ENABLE_FAILURE_SIMULATION"] = "true"
os.environ["DEFAULT_SYSTEM_PROMPT"] = "You are a test assistant."
os.environ["CACHE_TTL_SECONDS"] = "3600"
os.environ["LLM_TIMEOUT_SECONDS"] = "5"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

import litellm
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.llm_gateway import build_simulated_error, setup_llm_cache
from app.main import app


@pytest.fixture
def fake_llm(monkeypatch):
    state = {"calls": [], "failing_keys": {}}
    real_completion = litellm.completion

    def fake_completion(**kwargs):
        state["calls"].append(kwargs)
        failing_status = state["failing_keys"].get(kwargs["api_key"])
        if failing_status and "mock_response" not in kwargs:
            kwargs["mock_response"] = build_simulated_error(failing_status, "test")
        kwargs.setdefault("mock_response", "Reply to: " + kwargs["messages"][-1]["content"])
        return real_completion(**kwargs)

    monkeypatch.setattr(litellm, "completion", fake_completion)
    setup_llm_cache()
    return state


@pytest.fixture
def client(tmp_path, monkeypatch, fake_llm):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def send_message(client):
    def send(session_id, message, **extra_fields):
        body = {"session_id": session_id, "message": message, **extra_fields}
        return client.post("/chat", json=body)

    return send
