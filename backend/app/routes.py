from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from app import database
from app.chat_service import get_chat_history, handle_chat_request
from app.config import settings
from app.llm_gateway import is_cache_enabled
from app.schemas import ChatRequest

router = APIRouter()


@router.get("/health")
def health():
    if not database.is_database_reachable():
        return JSONResponse(status_code=503, content={"detail": "database unavailable"})
    return {
        "status": "ok",
        "keys_configured": len(settings.llm_api_keys),
        "cache_enabled": is_cache_enabled(),
        "model": settings.llm_model,
        "failure_simulation_enabled": settings.enable_failure_simulation,
    }


@router.post("/chat")
def chat(chat_request: ChatRequest, x_simulate_failure: str | None = Header(default=None)):
    return handle_chat_request(chat_request, x_simulate_failure)


@router.get("/sessions/{session_id}/messages")
def session_messages(session_id: str):
    history = get_chat_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session_id": session_id, "messages": history}
