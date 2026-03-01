# ============================================================
# Schema read: product/debate-engine/pipeline/schema.md
# Source commit: 91326d4 (task-014, 2026-03-01)
# Pipeline role: Agent B — implementation
#
# Endpoints implemented:
#   1. POST   /api/v1/debates                         → 201
#   2. GET    /api/v1/debates                         → 200
#   3. GET    /api/v1/debates/{debate_id}             → 200 / 404
#   4. POST   /api/v1/debates/{debate_id}/arguments   → 201 / 404
#   5. GET    /api/v1/debates/{debate_id}/arguments   → 200 / 404
#        (supports optional ?side= query parameter)
# ============================================================

from datetime import datetime, timezone
from typing import List, Literal, Optional
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_debates: dict[str, dict] = {}
_arguments: dict[str, list] = {}  # debate_id → list of argument dicts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class DebateCreate(BaseModel):
    topic: str
    description: str


class Debate(BaseModel):
    id: str
    topic: str
    description: str
    created_at: str


class DebateList(BaseModel):
    debates: List[Debate]


class ArgumentCreate(BaseModel):
    side: Literal["for", "against"]
    content: str


class Argument(BaseModel):
    id: str
    debate_id: str
    side: Literal["for", "against"]
    content: str
    created_at: str


class ArgumentList(BaseModel):
    arguments: List[Argument]


# ---------------------------------------------------------------------------
# Exception handlers — keep all error envelopes as {"error": "..."}
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Unprocessable Entity"},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/debates", status_code=201, response_model=Debate)
def create_debate(body: DebateCreate):
    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "topic": body.topic,
        "description": body.description,
        "created_at": _utcnow(),
    }
    _debates[debate_id] = debate
    _arguments[debate_id] = []
    return debate


@app.get("/api/v1/debates", status_code=200, response_model=DebateList)
def list_debates():
    sorted_debates = sorted(
        _debates.values(), key=lambda d: d["created_at"], reverse=True
    )
    return {"debates": sorted_debates}


@app.get("/api/v1/debates/{debate_id}", status_code=200, response_model=Debate)
def get_debate(debate_id: str):
    debate = _debates.get(debate_id)
    if debate is None:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})
    return debate


@app.post(
    "/api/v1/debates/{debate_id}/arguments",
    status_code=201,
    response_model=Argument,
)
def create_argument(debate_id: str, body: ArgumentCreate):
    if debate_id not in _debates:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})
    argument = {
        "id": str(uuid.uuid4()),
        "debate_id": debate_id,
        "side": body.side,
        "content": body.content,
        "created_at": _utcnow(),
    }
    _arguments[debate_id].append(argument)
    return argument


@app.get(
    "/api/v1/debates/{debate_id}/arguments",
    status_code=200,
    response_model=ArgumentList,
)
def list_arguments(
    debate_id: str,
    side: Optional[Literal["for", "against"]] = None,
):
    if debate_id not in _debates:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})
    args = _arguments[debate_id]
    if side is not None:
        args = [a for a in args if a["side"] == side]
    args_sorted = sorted(args, key=lambda a: a["created_at"])
    return {"arguments": args_sorted}
