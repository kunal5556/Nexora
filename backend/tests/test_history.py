def test_history_returns_messages_oldest_first(client, send_message):
    send_message("session-a", "First question")
    send_message("session-a", "Second question")

    response = client.get("/sessions/session-a/messages")

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "session-a"
    assert [(message["role"], message["content"]) for message in body["messages"]] == [
        ("user", "First question"),
        ("assistant", "Reply to: First question"),
        ("user", "Second question"),
        ("assistant", "Reply to: Second question"),
    ]


def test_history_has_metadata_only_on_assistant_messages(client, send_message):
    chat_metadata = send_message("session-a", "Hello").json()["metadata"]

    user_message, assistant_message = client.get("/sessions/session-a/messages").json()["messages"]

    assert "metadata" not in user_message
    assert assistant_message["metadata"] == chat_metadata


def test_history_excludes_system_prompt(client, send_message):
    send_message("session-a", "Hello", system_prompt="Answer like a pirate.")

    messages = client.get("/sessions/session-a/messages").json()["messages"]

    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert all("pirate" not in message["content"] for message in messages)


def test_unknown_session_returns_404(client):
    response = client.get("/sessions/does-not-exist/messages")

    assert response.status_code == 404
    assert response.json() == {"detail": "session not found"}
