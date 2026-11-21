from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_LENGTH = 4000
MAX_SYSTEM_PROMPT_LENGTH = 4000


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str
    system_prompt: str | None = None

    @field_validator("session_id")
    @classmethod
    def session_id_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("session_id must not be blank")
        return value

    @field_validator("message")
    @classmethod
    def message_must_have_valid_length(cls, value):
        trimmed_message = value.strip()
        if not 1 <= len(trimmed_message) <= MAX_MESSAGE_LENGTH:
            raise ValueError("message must be between 1 and 4000 characters after trimming whitespace")
        return trimmed_message

    @field_validator("system_prompt")
    @classmethod
    def clean_system_prompt(cls, value):
        if value is None:
            return None
        trimmed_prompt = value.strip()
        if len(trimmed_prompt) > MAX_SYSTEM_PROMPT_LENGTH:
            raise ValueError("system_prompt must be at most 4000 characters")
        return trimmed_prompt or None
