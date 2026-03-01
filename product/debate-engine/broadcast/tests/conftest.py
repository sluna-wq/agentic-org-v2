"""
Stub FastAPI application that conforms to the API contract assumed by test_api.py.

This file serves two purposes:
1. Makes tests self-contained — `pytest product/debate-engine/broadcast/tests/` runs
   without any other agent's files present.
2. Documents a runnable reference implementation of the API contract.

To run tests against a real implementation instead, replace the `app` import below
with an import from the actual api module:
    from product.debate_engine.broadcast.api import app
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# In-memory stub implementation
# ---------------------------------------------------------------------------

app = FastAPI(title="Debate Engine (Stub)")

_debates: dict = {}
_arguments: dict = {}


class DebateIn(BaseModel):
    title: str
    description: str = ""


class ArgumentIn(BaseModel):
    content: str
    position: str  # "for" | "against"


@app.post("/debates", status_code=201)
def create_debate(body: DebateIn):
    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "title": body.title,
        "description": body.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _debates[debate_id] = debate
    return debate


@app.get("/debates")
def list_debates():
    return list(_debates.values())


@app.get("/debates/{debate_id}")
def get_debate(debate_id: str):
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    return _debates[debate_id]


@app.post("/debates/{debate_id}/arguments", status_code=201)
def create_argument(debate_id: str, body: ArgumentIn):
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    arg_id = str(uuid.uuid4())
    argument = {
        "id": arg_id,
        "debate_id": debate_id,
        "content": body.content,
        "position": body.position,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _arguments.setdefault(debate_id, []).append(argument)
    return argument


@app.get("/debates/{debate_id}/arguments")
def list_arguments(debate_id: str):
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    return _arguments.get(debate_id, [])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """TestClient with clean in-memory state for each test."""
    _debates.clear()
    _arguments.clear()
    with TestClient(app) as c:
        yield c
