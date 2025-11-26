"""FastAPI application for Aegra (Agent Protocol Server)"""

import asyncio
import os
import sys
import json
import requests
from uuid import uuid4
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from langgraph_sdk import get_client, get_sync_client
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

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

from .middleware import DoubleEncodedJSONMiddleware, StructLogMiddleware
from .utils.setup_logging import setup_logging

# Task management for run cancellation
active_runs: dict[str, asyncio.Task] = {}

setup_logging()
logger = structlog.getLogger(__name__)


AEGRA_URL = os.getenv("AEGRA_URL")
logger.info(f"AEGRA_URL={AEGRA_URL}")

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

class AgentRequest(BaseModel):
    thread_id: str = ""
    assistant_id: str
    input: dict[str, Any]
    config: dict[str, Any] | None = {}
    context: dict[str, Any] | None = {}
    user_id: str = ""
    stream_mode: list[str] = ["messages"]

class AgentResponse(BaseModel):
    thread_id: str = None
    assistant_id: str
    input: dict[str, Any]
    config: dict[str, Any] | None = {}
    context: dict[str, Any] | None = {}
    user_id: str = None

@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Light Server", "version": "0.1.0", "status": "running"}

@app.post("/threads")
async def create_thread() -> dict[str, str]:
    client = get_client(url=AEGRA_URL)
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    return {"thread_id":thread_id}

@app.post("/threads/runs/stream")
async def thread_run_stream(request: AgentRequest) -> StreamingResponse:
    def inner_stream_func():
        client = get_sync_client(url=AEGRA_URL)
        thread_id = request.thread_id
        if thread_id is None or len(thread_id) == 0:
            thread = client.threads.create()
            thread_id = thread["thread_id"]

        stream = client.runs.stream(
            thread_id=thread_id,
            assistant_id=request.assistant_id,
            input=request.input,
            stream_mode=["messages-tuple"],
        )

        for chunk in stream:
            if chunk.event != "messages":
                continue
            res = chunk.data[0]
            if res["type"] in ["AIMessageChunk", "ai"]:
                yield res["content"]

    return StreamingResponse(
        inner_stream_func(),
        media_type="text/event-stream",
        headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Last-Event-ID",
        }
    )

@app.post("/threads/runs/wait")
async def thread_run_wait(request: AgentRequest):
    client = get_sync_client(url=AEGRA_URL)
    thread_id = request.thread_id
    if thread_id is None:
        thread = client.threads.create()
        thread_id = thread["thread_id"]
    response = client.runs.wait(
        thread_id=thread_id,
        assistant_id=request.assistant_id,
        input=request.input,
    )

    return response["messages"][-1]["content"]

if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.getenv("PORT", "8100"))
    uvicorn.run(app, host="0.0.0.0", port=port)
