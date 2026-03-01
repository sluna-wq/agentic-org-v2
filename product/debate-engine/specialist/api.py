# Debate Engine API — FastAPI Implementation (Agent B, Specialist Topology)
#
# Schema source : product/debate-engine/specialist/schema.md
# Schema commit : 7da7b3cb8e319e233b5fc7d2de17faeba10a1ac6
#                 (task-020: write specialist Agent A schema for Debate Engine)
#
# Endpoints implemented:
#   1. POST   /api/v1/debates                        -> 201 Created
#   2. GET    /api/v1/debates                        -> 200 OK
#   3. GET    /api/v1/debates/{debate_id}            -> 200 OK / 404 Not Found
#   4. POST   /api/v1/debates/{debate_id}/arguments  -> 201 Created / 404 Not Found
#   5. GET    /api/v1/debates/{debate_id}/arguments  -> 200 OK / 404 Not Found
#              (?side= filter; 422 for invalid side value)
#
# Implementation Notes:
#
# 1. Literal["for", "against"] for side validation — using a Literal type annotation
#    is more idiomatic than a custom @field_validator for a fixed enum of values.
#    It self-documents in the OpenAPI schema, participates in static analysis, and
#    FastAPI surfaces the constraint in generated docs. For the ?side= query parameter,
#    Pydantic validates it before the endpoint body executes, so the schema-mandated
#    "422 before 404" ordering for invalid side values is guaranteed automatically by
#    FastAPI's request processing pipeline — no manual ordering code required.
#
# 2. Dynamic argument_count computation — argument_count is derived on-the-fly by
#    counting matching entries in _arguments rather than maintaining a mutable counter
#    on each stored Debate record. With in-memory storage the cost is negligible, and
#    we eliminate an entire class of consistency bugs (counter drift on mid-update
#    exceptions, concurrent writes, etc.). The schema specifies argument_count must
#    "equal the total number of Arguments in the database with that debate_id" — a
#    derived property is the only way to guarantee that invariant without transactions.
#
# 3. Typed response models (DebateOut, ArgumentOut) — returning Pydantic model
#    instances rather than raw dicts or hand-constructed JSONResponse payloads gives
#    FastAPI accurate OpenAPI documentation, enforces the serialization contract at the
#    type level, and avoids silent field omissions or extra fields leaking through.
#    Request and response models are intentionally kept separate: DebateCreate has no
#    id or created_at; DebateOut never accepts client-supplied values for those fields.

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(title="Debate Engine", version="1.0.0")

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Return {"error": "..."} for all HTTP errors (404, etc.)."""
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return {"error": "..."} for all 422 validation errors (overrides FastAPI default)."""
    errors = exc.errors()
    msg = "Validation error"
    if errors:
        raw = errors[0].get("msg", msg)
        # Pydantic v2 prefixes custom ValueError messages with "Value error, "
        msg = raw.removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"error": msg})


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

# Stored debate records omit argument_count (computed dynamically on read).
_debates: dict[str, dict] = {}  # debate_id -> {id, title, description, created_at}
_arguments: list[dict] = []     # [{id, debate_id, side, body, created_at}, ...] in insertion order


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    """Current UTC time as ISO 8601 string with microseconds and Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def _build_debate_out(debate: dict) -> DebateOut:
    """Attach computed argument_count and return a DebateOut response model."""
    count = sum(1 for a in _arguments if a["debate_id"] == debate["id"])
    return DebateOut(**debate, argument_count=count)


# ---------------------------------------------------------------------------
# Pydantic request models — only client-supplied fields
# ---------------------------------------------------------------------------

class DebateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class ArgumentCreate(BaseModel):
    side: Literal["for", "against"]
    body: str = Field(..., min_length=1, max_length=2000)


# ---------------------------------------------------------------------------
# Pydantic response models — exact field names per schema contract
# ---------------------------------------------------------------------------

class DebateOut(BaseModel):
    id: str
    title: str
    description: str
    argument_count: int
    created_at: str


class ArgumentOut(BaseModel):
    id: str
    debate_id: str
    side: str
    body: str
    created_at: str


class DebateListOut(BaseModel):
    debates: list[DebateOut]
    total: int


class ArgumentListOut(BaseModel):
    arguments: list[ArgumentOut]
    total: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/debates", status_code=201, response_model=DebateOut)
async def create_debate(payload: DebateCreate) -> DebateOut:
    """POST /api/v1/debates → 201 Created / 422 Unprocessable Entity"""
    debate_id = str(uuid.uuid4())
    record = {
        "id": debate_id,
        "title": payload.title,
        "description": payload.description,
        "created_at": _utc_now(),
    }
    _debates[debate_id] = record
    return _build_debate_out(record)


@app.get("/api/v1/debates", status_code=200, response_model=DebateListOut)
async def list_debates() -> DebateListOut:
    """GET /api/v1/debates → 200 OK (ordered by created_at descending, newest first)"""
    sorted_debates = sorted(
        (_build_debate_out(d) for d in _debates.values()),
        key=lambda d: d.created_at,
        reverse=True,
    )
    return DebateListOut(debates=sorted_debates, total=len(sorted_debates))


@app.get("/api/v1/debates/{debate_id}", status_code=200, response_model=DebateOut)
async def get_debate(debate_id: str) -> DebateOut:
    """GET /api/v1/debates/{debate_id} → 200 OK / 404 Not Found"""
    record = _debates.get(debate_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    return _build_debate_out(record)


@app.post(
    "/api/v1/debates/{debate_id}/arguments",
    status_code=201,
    response_model=ArgumentOut,
)
async def create_argument(debate_id: str, payload: ArgumentCreate) -> ArgumentOut:
    """POST /api/v1/debates/{debate_id}/arguments → 201 Created / 404 Not Found / 422

    Debate existence is checked before argument storage; a missing debate returns 404
    even when the payload is valid.
    """
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")

    arg_id = str(uuid.uuid4())
    record = {
        "id": arg_id,
        "debate_id": debate_id,   # always from path param, never from request body
        "side": payload.side,
        "body": payload.body,
        "created_at": _utc_now(),
    }
    _arguments.append(record)
    return ArgumentOut(**record)


@app.get(
    "/api/v1/debates/{debate_id}/arguments",
    status_code=200,
    response_model=ArgumentListOut,
)
async def list_arguments(
    debate_id: str,
    side: Optional[Literal["for", "against"]] = Query(default=None),
) -> ArgumentListOut:
    """GET /api/v1/debates/{debate_id}/arguments → 200 OK / 404 Not Found

    ?side= filter:
      - omitted  → return all arguments for this debate
      - "for"    → return only "for" arguments
      - "against"→ return only "against" arguments
      - any other value → 422 (raised automatically by Pydantic Literal constraint
        on the Query param, before debate existence is checked)
    """
    if debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")

    # Arguments ordered oldest first (ascending) — chronological debate flow
    result = [
        ArgumentOut(**a)
        for a in _arguments
        if a["debate_id"] == debate_id and (side is None or a["side"] == side)
    ]
    return ArgumentListOut(arguments=result, total=len(result))
