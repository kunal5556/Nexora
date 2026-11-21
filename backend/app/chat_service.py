import json
import time

from app import database
from app.config import settings
from app.llm_gateway import ask_llm


def choose_system_prompt(session_id, requested_prompt):
    if requested_prompt:
        return requested_prompt
    return database.get_session_system_prompt(session_id) or settings.default_system_prompt


def build_llm_messages(system_prompt, history_rows, user_message):
    messages = [{"role": "system", "content": system_prompt}]
    for row in history_rows:
        messages.append({"role": row["role"], "content": row["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages


def handle_chat_request(chat_request):
    started_at = time.perf_counter()
    system_prompt = choose_system_prompt(chat_request.session_id, chat_request.system_prompt)
    history_rows = database.get_session_messages(chat_request.session_id)
    llm_messages = build_llm_messages(system_prompt, history_rows, chat_request.message)

    result = ask_llm(llm_messages, {})
    metadata = {
        "resolution_source": "LLM_CACHE" if result.from_cache else "LIVE_INFERENCE",
        "model": settings.llm_model,
        "latency_ms": int((time.perf_counter() - started_at) * 1000),
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "key_id": result.key_id,
        "fallback_attempts": result.fallback_attempts,
    }
    database.save_chat_exchange(
        chat_request.session_id,
        chat_request.message,
        result.reply,
        metadata,
        chat_request.system_prompt,
    )
    return {"session_id": chat_request.session_id, "reply": result.reply, "metadata": metadata}


def get_chat_history(session_id):
    history = []
    for row in database.get_session_messages(session_id):
        message = {"role": row["role"], "content": row["content"]}
        if row["metadata"]:
            message["metadata"] = json.loads(row["metadata"])
        history.append(message)
    return history
