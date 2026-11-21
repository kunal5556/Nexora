from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import database
from app.config import settings

router = APIRouter()


@router.get("/health")
def health():
    if not database.is_database_reachable():
        return JSONResponse(status_code=503, content={"detail": "database unavailable"})
    return {
        "status": "ok",
        "keys_configured": len(settings.llm_api_keys),
        "model": settings.llm_model,
        "failure_simulation_enabled": settings.enable_failure_simulation,
    }
