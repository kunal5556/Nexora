import pytest

INVALID_BODIES = [
    pytest.param({"session_id": "invalid-1"}, id="missing message"),
    pytest.param({"session_id": "invalid-1", "message": ""}, id="empty message"),
    pytest.param({"session_id": "invalid-1", "message": "   "}, id="whitespace message"),
    pytest.param({"session_id": "invalid-1", "message": "  " + "a" * 4001 + "  "}, id="message over 4000 chars"),
    pytest.param({"session_id": "invalid-1", "message": 123}, id="message not a string"),
    pytest.param({"message": "Hello"}, id="missing session_id"),
    pytest.param({"session_id": "", "message": "Hello"}, id="empty session_id"),
    pytest.param({"session_id": "   ", "message": "Hello"}, id="blank session_id"),
    pytest.param({"session_id": "s" * 129, "message": "Hello"}, id="session_id over 128 chars"),
    pytest.param({"session_id": "invalid-1", "message": "Hello", "system_prompt": "p" * 4001}, id="long system_prompt"),
]


@pytest.mark.parametrize("body", INVALID_BODIES)
def test_invalid_chat_requests_return_422_and_store_nothing(client, fake_llm, body):
    response = client.post("/chat", json=body)

    assert response.status_code == 422
    assert "detail" in response.json()
    assert fake_llm["calls"] == []
    assert client.get("/sessions/invalid-1/messages").status_code == 404


def test_malformed_json_returns_422(client):
    response = client.post("/chat", content="{bad json", headers={"Content-Type": "application/json"})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_message_with_4000_characters_after_trimming_is_accepted(client, send_message):
    response = send_message("long-message", "  " + "a" * 4000 + "  ")

    assert response.status_code == 200
    stored_message = client.get("/sessions/long-message/messages").json()["messages"][0]
    assert len(stored_message["content"]) == 4000


def test_session_id_with_128_characters_is_accepted(send_message):
    session_id = "s" * 128

    response = send_message(session_id, "Hello")

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
