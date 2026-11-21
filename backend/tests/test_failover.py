import pytest

from app.config import settings

ALL_UNAVAILABLE = {"detail": "all providers unavailable"}


def simulate(header_value):
    return {"X-Simulate-Failure": header_value}


@pytest.mark.parametrize("status", [429, 500, 502, 503])
def test_simulated_failure_on_key_1_uses_key_2(send_message, status):
    response = send_message("session-a", "Hello", headers=simulate(f"key_1={status}"))

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Reply to: Hello"
    assert body["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert body["metadata"]["key_id"] == "key_2"
    assert body["metadata"]["fallback_attempts"] == 1


def test_simulated_failure_on_every_key_returns_503_and_stores_nothing(client, send_message):
    response = send_message("session-c", "Hello", headers=simulate("*=429"))

    assert response.status_code == 503
    assert response.json() == ALL_UNAVAILABLE
    assert client.get("/sessions/session-c/messages").status_code == 404


def test_simulated_failure_on_both_keys_returns_503(send_message):
    response = send_message("session-c", "Hello", headers=simulate("key_1=429,key_2=500"))

    assert response.status_code == 503
    assert response.json() == ALL_UNAVAILABLE


def test_simulated_request_skips_cache_read(send_message):
    send_message("session-a", "Cached question")

    metadata = send_message("session-b", "Cached question", headers=simulate("key_1=429")).json()["metadata"]

    assert metadata["resolution_source"] == "LIVE_INFERENCE"
    assert metadata["key_id"] == "key_2"
    assert metadata["fallback_attempts"] == 1


def test_simulation_affects_only_that_request(send_message):
    send_message("session-a", "First question", headers=simulate("key_1=429"))

    metadata = send_message("session-a", "Second question").json()["metadata"]

    assert metadata["resolution_source"] == "LIVE_INFERENCE"
    assert metadata["key_id"] == "key_1"
    assert metadata["fallback_attempts"] == 0


def test_simulation_header_is_ignored_when_switch_is_off(send_message, monkeypatch):
    monkeypatch.setattr(settings, "enable_failure_simulation", False)

    response = send_message("session-a", "Hello", headers=simulate("*=429"))

    assert response.status_code == 200
    assert response.json()["metadata"]["key_id"] == "key_1"


def test_real_rate_limit_on_first_key_falls_back_to_second_key(send_message, fake_llm):
    fake_llm["failing_keys"] = {"test-key-one": 429}

    metadata = send_message("session-a", "Hello").json()["metadata"]

    assert metadata["key_id"] == "key_2"
    assert metadata["fallback_attempts"] == 1


def test_real_failure_on_all_keys_returns_503(client, send_message, fake_llm):
    fake_llm["failing_keys"] = {"test-key-one": 429, "test-key-two": 500}

    response = send_message("session-c", "Hello")

    assert response.status_code == 503
    assert response.json() == ALL_UNAVAILABLE
    assert client.get("/sessions/session-c/messages").status_code == 404
