METADATA_FIELDS = {
    "resolution_source",
    "model",
    "latency_ms",
    "input_tokens",
    "output_tokens",
    "key_id",
    "fallback_attempts",
}


def test_first_message_is_live_inference(send_message):
    response = send_message("session-a", "What is the capital of France?")

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "session-a"
    assert body["reply"] == "Reply to: What is the capital of France?"
    metadata = body["metadata"]
    assert set(metadata) == METADATA_FIELDS
    assert metadata["resolution_source"] == "LIVE_INFERENCE"
    assert metadata["model"] == "gemini/gemini-3.5-flash-lite"
    assert metadata["key_id"] == "key_1"
    assert metadata["fallback_attempts"] == 0
    assert isinstance(metadata["input_tokens"], int)
    assert isinstance(metadata["output_tokens"], int)


def test_same_first_message_in_new_session_comes_from_cache(send_message):
    first = send_message("session-a", "What is the capital of France?").json()
    second = send_message("session-b", "What is the capital of France?").json()

    assert second["metadata"]["resolution_source"] == "LLM_CACHE"
    assert second["reply"] == first["reply"]
    assert second["metadata"]["key_id"] is None
    assert second["metadata"]["fallback_attempts"] == 0
    assert second["metadata"]["input_tokens"] == first["metadata"]["input_tokens"]
    assert second["metadata"]["output_tokens"] == first["metadata"]["output_tokens"]


def test_different_message_is_not_served_from_cache(send_message):
    send_message("session-a", "What is the capital of France?")
    second = send_message("session-b", "What is the capital of Spain?").json()

    assert second["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert second["reply"] == "Reply to: What is the capital of Spain?"


def test_follow_up_message_sends_full_history_to_llm(send_message, fake_llm):
    send_message("session-a", "My name is Priya.")
    send_message("session-a", "What is my name?")

    assert fake_llm["calls"][-1]["messages"] == [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "My name is Priya."},
        {"role": "assistant", "content": "Reply to: My name is Priya."},
        {"role": "user", "content": "What is my name?"},
    ]


def test_sessions_are_kept_separate(send_message, fake_llm):
    send_message("session-a", "The secret word is mango.")
    send_message("session-b", "Hello")

    assert fake_llm["calls"][-1]["messages"] == [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Hello"},
    ]


def test_tokens_are_reported_per_request(send_message):
    first = send_message("session-a", "First question").json()
    second = send_message("session-a", "Second question").json()

    assert second["metadata"]["input_tokens"] == first["metadata"]["input_tokens"]
    assert second["metadata"]["output_tokens"] == first["metadata"]["output_tokens"]


def test_default_system_prompt_is_used_without_override(send_message, fake_llm):
    send_message("session-a", "Hello")

    assert fake_llm["calls"][-1]["messages"][0] == {"role": "system", "content": "You are a test assistant."}


def test_system_prompt_override_is_used_and_kept_for_session(send_message, fake_llm):
    send_message("session-a", "Hello", system_prompt="  Answer like a pirate.  ")
    send_message("session-a", "How are you?")

    first_call_prompt = fake_llm["calls"][0]["messages"][0]
    second_call_prompt = fake_llm["calls"][-1]["messages"][0]
    assert first_call_prompt == {"role": "system", "content": "Answer like a pirate."}
    assert second_call_prompt == {"role": "system", "content": "Answer like a pirate."}


def test_api_keys_are_never_returned(client, send_message):
    chat_text = send_message("session-a", "Hello").text
    history_text = client.get("/sessions/session-a/messages").text

    for api_key in ["test-key-one", "test-key-two"]:
        assert api_key not in chat_text
        assert api_key not in history_text


def test_latency_is_an_integer(send_message):
    metadata = send_message("session-a", "Hello").json()["metadata"]

    assert isinstance(metadata["latency_ms"], int)
    assert metadata["latency_ms"] >= 0
