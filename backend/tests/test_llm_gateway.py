import pytest

from app.llm_gateway import AllProvidersUnavailableError, ask_llm


def build_messages(text):
    return [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": text},
    ]


def test_first_call_is_live_and_uses_key_1(fake_llm):
    result = ask_llm(build_messages("What is the capital of France?"), {})

    assert result.reply == "Reply to: What is the capital of France?"
    assert result.from_cache is False
    assert result.key_id == "key_1"
    assert result.fallback_attempts == 0
    assert result.input_tokens > 0
    assert result.output_tokens > 0


def test_repeated_messages_come_from_cache(fake_llm):
    first_result = ask_llm(build_messages("Hello there"), {})
    second_result = ask_llm(build_messages("Hello there"), {})

    assert second_result.from_cache is True
    assert second_result.key_id is None
    assert second_result.fallback_attempts == 0
    assert second_result.reply == first_result.reply
    assert second_result.input_tokens == first_result.input_tokens
    assert second_result.output_tokens == first_result.output_tokens


def test_different_messages_are_not_cached(fake_llm):
    ask_llm(build_messages("First question"), {})
    second_result = ask_llm(build_messages("Second question"), {})

    assert second_result.from_cache is False
    assert second_result.reply == "Reply to: Second question"


def test_failed_first_key_falls_over_to_second_key(fake_llm):
    fake_llm["failing_keys"] = {"test-key-one": 429}

    result = ask_llm(build_messages("Hello"), {})

    assert result.from_cache is False
    assert result.key_id == "key_2"
    assert result.fallback_attempts == 1


def test_all_keys_failing_raises_all_providers_unavailable(fake_llm):
    fake_llm["failing_keys"] = {"test-key-one": 429, "test-key-two": 503}

    with pytest.raises(AllProvidersUnavailableError):
        ask_llm(build_messages("Hello"), {})


def test_simulated_failure_skips_cache_and_uses_next_key(fake_llm):
    ask_llm(build_messages("Cached question"), {})

    result = ask_llm(build_messages("Cached question"), {"key_1": 429})

    assert result.from_cache is False
    assert result.key_id == "key_2"
    assert result.fallback_attempts == 1


def test_keys_are_tried_in_order_without_retries(fake_llm):
    fake_llm["failing_keys"] = {"test-key-one": 500}

    ask_llm(build_messages("Hello"), {})

    assert [call["api_key"] for call in fake_llm["calls"]] == ["test-key-one", "test-key-two"]
    assert all(call["num_retries"] == 0 for call in fake_llm["calls"])
