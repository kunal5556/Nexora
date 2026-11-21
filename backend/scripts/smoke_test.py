import json
import sys
import time
import urllib.error
import urllib.request
import uuid

METADATA_FIELDS = {
    "resolution_source",
    "model",
    "latency_ms",
    "input_tokens",
    "output_tokens",
    "key_id",
    "fallback_attempts",
}

results = []


def send_request(method, url, body=None, headers=None, raw_body=None):
    data = raw_body
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    started_at = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            status_code, content = response.status, response.read()
    except urllib.error.HTTPError as error:
        status_code, content = error.code, error.read()
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"      could not reach {url}: {error}")
        status_code, content = 0, b""
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    try:
        payload = json.loads(content)
    except ValueError:
        payload = None
    return status_code, payload or {}, elapsed_ms


def post_chat(base_url, session_id, message, headers=None):
    body = {"session_id": session_id, "message": message}
    return send_request("POST", f"{base_url}/chat", body=body, headers=headers)


def check(description, condition):
    results.append(condition)
    print(("PASS  " if condition else "FAIL  ") + description)


def check_health(base_url):
    status_code, health, _ = send_request("GET", f"{base_url}/health")
    check("GET /health returns 200", status_code == 200)
    check("health status is ok", health.get("status") == "ok")
    check("at least 2 keys are configured", (health.get("keys_configured") or 0) >= 2)
    check("cache is enabled", health.get("cache_enabled") is True)
    return health


def check_live_and_cache(base_url, run_id, first_message):
    status_code, first, _ = post_chat(base_url, f"smoke-{run_id}-a", first_message)
    first_metadata = first.get("metadata", {})
    check("first message returns 200 with a non-empty reply", status_code == 200 and bool(first.get("reply")))
    check("metadata has all 7 fields", METADATA_FIELDS <= set(first_metadata))
    check(
        f"first message is LIVE_INFERENCE (answered by {first_metadata.get('key_id')})",
        first_metadata.get("resolution_source") == "LIVE_INFERENCE" and str(first_metadata.get("key_id")).startswith("key_"),
    )
    integer_fields = ["latency_ms", "input_tokens", "output_tokens", "fallback_attempts"]
    check("latency, tokens and fallback attempts are integers", all(isinstance(first_metadata.get(field), int) for field in integer_fields))

    _, second, _ = post_chat(base_url, f"smoke-{run_id}-b", first_message)
    second_metadata = second.get("metadata", {})
    check("same first message in a new session is LLM_CACHE", second_metadata.get("resolution_source") == "LLM_CACHE")
    check("cache hit returns the identical reply", second.get("reply") == first.get("reply"))
    check("cache hit has key_id null and 0 fallback attempts", second_metadata.get("key_id") is None and second_metadata.get("fallback_attempts") == 0)
    check(
        "cache hit reports the stored token usage",
        (second_metadata.get("input_tokens"), second_metadata.get("output_tokens"))
        == (first_metadata.get("input_tokens"), first_metadata.get("output_tokens")),
    )
    check(
        f"cache hit is faster ({second_metadata.get('latency_ms')} ms vs {first_metadata.get('latency_ms')} ms)",
        (second_metadata.get("latency_ms") or 0) < (first_metadata.get("latency_ms") or 0),
    )
    return first_metadata


def check_multi_turn(base_url, run_id, first_metadata):
    session_id = f"smoke-{run_id}-a"
    post_chat(base_url, session_id, "My favourite colour is teal. Please remember it.")
    status_code, answer, _ = post_chat(base_url, session_id, "What is my favourite colour? Answer in one word.")
    answer_metadata = answer.get("metadata", {})
    check(f"bot remembers earlier messages (reply: {answer.get('reply')!r})", status_code == 200 and "teal" in str(answer.get("reply")).lower())
    check(
        "follow-up input_tokens include the history",
        (answer_metadata.get("input_tokens") or 0) > (first_metadata.get("input_tokens") or 0),
    )


def check_history(base_url, run_id, first_message):
    status_code, history, _ = send_request("GET", f"{base_url}/sessions/smoke-{run_id}-a/messages")
    messages = history.get("messages", [])
    check("history returns 200 with 6 messages", status_code == 200 and len(messages) == 6)
    check("history alternates user and assistant", [message.get("role") for message in messages] == ["user", "assistant"] * 3)
    check("history is oldest first", bool(messages) and messages[0].get("content") == first_message)
    check("only assistant messages have metadata", all(("metadata" in message) == (message.get("role") == "assistant") for message in messages))

    status_code, body, _ = send_request("GET", f"{base_url}/sessions/unknown-{run_id}/messages")
    check("unknown session returns 404 session not found", status_code == 404 and body == {"detail": "session not found"})


def check_validation(base_url, run_id):
    session_id = f"smoke-{run_id}-v"
    cases = [
        ("whitespace-only message returns 422", {"session_id": session_id, "message": "   "}, None),
        ("4001-character message returns 422", {"session_id": session_id, "message": "a" * 4001}, None),
        ("missing session_id returns 422", {"message": "Hello"}, None),
        ("malformed JSON returns 422", None, b"{bad json"),
    ]
    for description, body, raw_body in cases:
        status_code, payload, _ = send_request("POST", f"{base_url}/chat", body=body, raw_body=raw_body)
        check(description, status_code == 422 and "detail" in payload)


def check_failover(base_url, run_id, health):
    if not health.get("failure_simulation_enabled"):
        check("failure simulation is enabled on this backend", False)
        return

    for status in [429, 500]:
        headers = {"X-Simulate-Failure": f"key_1={status}"}
        message = f"Smoke {run_id}: name one primary colour ({status})."
        status_code, body, _ = post_chat(base_url, f"smoke-{run_id}-f{status}", message, headers)
        metadata = body.get("metadata", {})
        check(
            f"key_1={status} is answered by key_2 with 1 fallback attempt",
            status_code == 200
            and bool(body.get("reply"))
            and metadata.get("resolution_source") == "LIVE_INFERENCE"
            and metadata.get("key_id") == "key_2"
            and metadata.get("fallback_attempts") == 1,
        )

    session_id = f"smoke-{run_id}-c"
    status_code, body, _ = post_chat(base_url, session_id, "This request should fail.", {"X-Simulate-Failure": "*=429"})
    check("*=429 returns 503 all providers unavailable", status_code == 503 and body == {"detail": "all providers unavailable"})
    status_code, _, _ = send_request("GET", f"{base_url}/sessions/{session_id}/messages")
    check("failed request was not added to history", status_code == 404)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/smoke_test.py <backend_base_url>")
        sys.exit(2)

    base_url = sys.argv[1].rstrip("/")
    run_id = uuid.uuid4().hex[:8]
    first_message = f"Smoke {run_id}: what is the capital of France?"
    print(f"Running smoke test {run_id} against {base_url}")

    health = check_health(base_url)
    first_metadata = check_live_and_cache(base_url, run_id, first_message)
    check_multi_turn(base_url, run_id, first_metadata)
    check_history(base_url, run_id, first_message)
    check_validation(base_url, run_id)
    check_failover(base_url, run_id, health)

    failed_count = results.count(False)
    if failed_count:
        print(f"{failed_count} of {len(results)} checks failed")
        sys.exit(1)
    print(f"All {len(results)} checks passed")


if __name__ == "__main__":
    main()
