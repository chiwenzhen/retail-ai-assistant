"""FastAPI application for Aegra (Agent Protocol Server)"""

import asyncio
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from langgraph_sdk import get_client, get_sync_client

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add graphs directory to Python path so react_agent can be imported
# This MUST happen before importing any modules that depend on graphs/
current_dir = Path(__file__).parent.parent.parent  # Go up to aegra root

# ruff: noqa: E402 - imports below require sys.path modification above
import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from .api.assistants import router as assistants_router
from .api.runs import router as runs_router
from .api.store import router as store_router
from .api.threads import router as threads_router
from .core.auth_middleware import get_auth_backend, on_auth_error
from .core.database import db_manager
from .core.health import router as health_router
from .middleware import DoubleEncodedJSONMiddleware, StructLogMiddleware
from .models.errors import AgentProtocolError, get_error_type
from .observability.base import get_observability_manager
from .observability.langfuse_integration import _langfuse_provider
from .services.event_store import event_store
from .services.langgraph_service import get_langgraph_service
from .utils.setup_logging import setup_logging

# Task management for run cancellation
active_runs: dict[str, asyncio.Task] = {}

setup_logging()
logger = structlog.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("light server startup...")

    yield

    logger.info("light server shutdown!")


# Create FastAPI application
app = FastAPI(
    title="Light Server",
    description="",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(StructLogMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to handle double-encoded JSON from frontend
app.add_middleware(DoubleEncodedJSONMiddleware)

@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Light Server", "version": "0.1.0", "status": "running"}

@app.get("/threads")
async def root() -> dict[str, str]:
    client = get_client(url="http://localhost:8000")
    return {"message": "light server", "version": "0.1.0", "status": "running"}


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.getenv("PORT", "8100"))
    uvicorn.run(app, host="0.0.0.0", port=port)
