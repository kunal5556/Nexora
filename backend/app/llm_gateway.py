import logging
import warnings
from dataclasses import dataclass

import litellm
from litellm.caching.caching import Cache

from app.config import settings

logger = logging.getLogger(__name__)

SIMULATED_ERROR_CLASSES = {
    429: litellm.RateLimitError,
    500: litellm.InternalServerError,
    502: litellm.BadGatewayError,
    503: litellm.ServiceUnavailableError,
}


class AllProvidersUnavailableError(Exception):
    pass


@dataclass
class LlmResult:
    reply: str
    from_cache: bool
    key_id: str | None
    fallback_attempts: int
    input_tokens: int
    output_tokens: int


def setup_llm_cache():
    warnings.filterwarnings("ignore", message="Pydantic serializer warnings")
    litellm.suppress_debug_info = True
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    litellm.cache = Cache(type="local", ttl=settings.cache_ttl_seconds)


def is_cache_enabled():
    return litellm.cache is not None


def build_simulated_error(status_code, key_id):
    error_class = SIMULATED_ERROR_CLASSES[status_code]
    return error_class(
        message=f"Simulated {status_code} error for {key_id}",
        llm_provider=settings.llm_model.split("/")[0],
        model=settings.llm_model,
    )


def read_token_usage(response, messages, reply):
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "prompt_tokens", None)
    output_tokens = getattr(usage, "completion_tokens", None)
    if input_tokens is None:
        input_tokens = litellm.token_counter(model=settings.llm_model, messages=messages)
    if output_tokens is None:
        output_tokens = litellm.token_counter(model=settings.llm_model, text=reply)
    return int(input_tokens), int(output_tokens)


def read_reply(response):
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""
    return (choices[0].message.content or "").strip()


def ask_llm(messages, simulated_failures):
    failed_attempts = 0
    skip_cache_read = bool(simulated_failures)
    for index, api_key in enumerate(settings.llm_api_keys):
        key_id = f"key_{index + 1}"
        request_args = {
            "model": settings.llm_model,
            "messages": messages,
            "api_key": api_key,
            "num_retries": 0,
            "timeout": settings.llm_timeout_seconds,
        }
        if skip_cache_read:
            request_args["cache"] = {"no-cache": True}
        if key_id in simulated_failures:
            request_args["mock_response"] = build_simulated_error(simulated_failures[key_id], key_id)

        try:
            response = litellm.completion(**request_args)
        except Exception as error:
            failed_attempts += 1
            logger.warning("%s failed with status %s, trying next key", key_id, getattr(error, "status_code", "unknown"))
            continue

        reply = read_reply(response)
        if not reply:
            failed_attempts += 1
            skip_cache_read = True
            logger.warning("%s returned an empty reply, trying next key", key_id)
            continue

        from_cache = response._hidden_params.get("cache_hit") is True
        input_tokens, output_tokens = read_token_usage(response, messages, reply)
        return LlmResult(
            reply=reply,
            from_cache=from_cache,
            key_id=None if from_cache else key_id,
            fallback_attempts=0 if from_cache else failed_attempts,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    raise AllProvidersUnavailableError()
