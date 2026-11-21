import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

SQLITE_URL_PREFIX = "sqlite:///"
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and concisely in plain text."


def read_list(name, default=""):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def read_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() == "true"


def database_path_from_url(database_url):
    if not database_url.startswith(SQLITE_URL_PREFIX):
        raise RuntimeError("DATABASE_URL must start with sqlite:///")
    return database_url[len(SQLITE_URL_PREFIX):]


@dataclass
class Settings:
    llm_api_keys: list[str]
    llm_model: str
    database_path: str
    allowed_origins: list[str]
    enable_failure_simulation: bool
    default_system_prompt: str
    cache_ttl_seconds: int
    llm_timeout_seconds: int

    @property
    def key_ids(self):
        return [f"key_{number}" for number in range(1, len(self.llm_api_keys) + 1)]


def load_settings():
    api_keys = read_list("LLM_API_KEYS")
    if len(api_keys) < 2:
        raise RuntimeError("LLM_API_KEYS must contain at least 2 comma-separated keys")
    return Settings(
        llm_api_keys=api_keys,
        llm_model=os.getenv("LLM_MODEL", "gemini/gemini-3.5-flash-lite").strip(),
        database_path=database_path_from_url(os.getenv("DATABASE_URL", "sqlite:///./data/app.db").strip()),
        allowed_origins=[origin.rstrip("/") for origin in read_list("ALLOWED_ORIGINS", "http://localhost:3000")],
        enable_failure_simulation=read_bool("ENABLE_FAILURE_SIMULATION"),
        default_system_prompt=os.getenv("DEFAULT_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT).strip(),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "86400")),
        llm_timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
    )


settings = load_settings()
