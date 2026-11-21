import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application):
    init_db()
    logger.info("Loaded %d API keys for model %s", len(settings.llm_api_keys), settings.llm_model)
    yield


app = FastAPI(title="LLM Chatbot API", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Simulate-Failure"],
)

app.include_router(router)


@app.exception_handler(Exception)
async def handle_unexpected_error(request, error):
    logger.exception("Unexpected error while handling %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "internal server error"})
