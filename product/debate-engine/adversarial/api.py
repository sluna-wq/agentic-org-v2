# Debate Engine API — Implementation (Agent B)
#
# Schema source : product/debate-engine/adversarial/schema.md
# Schema commit : ce18a57323bf423dbdd581ce7a2e3a12682a2f1c
#                 (task-017: add Debate Engine adversarial schema (Agent A))
#
# Endpoints implemented:
#   1. POST   /api/v1/debates                        -> 201 Created
#   2. GET    /api/v1/debates                        -> 200 OK
#   3. GET    /api/v1/debates/{debate_id}            -> 200 OK / 404 Not Found
#   4. POST   /api/v1/debates/{debate_id}/arguments  -> 201 Created / 404 Not Found
#   5. GET    /api/v1/debates/{debate_id}/arguments  -> 200 OK / 404 Not Found
#              (?side= filter; 422 for invalid side value)

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, field_validator

app = FastAPI()

# In-memory storage keyed by ID
_debates: dict[str, dict] = {}
_arguments: dict[str, dict] = {}


def _now_utc() -> str:
    """Return current UTC time as ISO 8601 string with microseconds ending in Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def _first_error_msg(exc: ValidationError) -> str:
    """Extract the first human-readable message from a Pydantic ValidationError."""
    errors = exc.errors()
    if not errors:
        return "Validation error"
    msg = errors[0].get("msg", "Validation error")
    # Pydantic v2 prefixes custom ValueError messages with "Value error, "
    if msg.startswith("Value error, "):
        msg = msg[len("Value error, "):]
    return msg


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class DebateCreate(BaseModel):
    title: str
    description: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 200:
            raise ValueError("title must be between 1 and 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 2000:
            raise ValueError("description must be between 1 and 2000 characters")
        return v


class ArgumentCreate(BaseModel):
    side: str
    body: str

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        if v not in ("for", "against"):
            raise ValueError("side must be 'for' or 'against'")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 1000:
            raise ValueError("body must be between 1 and 1000 characters")
        return v


# ---------------------------------------------------------------------------
# Custom 422 handler — overrides FastAPI default {"detail": [...]} shape
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        msg = errors[0].get("msg", "Validation error")
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
    else:
        msg = "Validation error"
    return JSONResponse(status_code=422, content={"error": msg})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/debates")
async def create_debate(request: Request):
    """POST /api/v1/debates → 201 Created / 422 Unprocessable Entity"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=422, content={"error": "Invalid JSON body"})

    try:
        payload = DebateCreate.model_validate(body)
    except ValidationError as exc:
        return JSONResponse(status_code=422, content={"error": _first_error_msg(exc)})

    debate_id = str(uuid.uuid4())
    debate = {
        "id": debate_id,
        "title": payload.title,
        "description": payload.description,
        "created_at": _now_utc(),
    }
    _debates[debate_id] = debate
    return JSONResponse(status_code=201, content=debate)


@app.get("/api/v1/debates")
async def list_debates():
    """GET /api/v1/debates → 200 OK (array, oldest first)"""
    sorted_list = sorted(_debates.values(), key=lambda d: d["created_at"])
    return JSONResponse(status_code=200, content=sorted_list)


@app.get("/api/v1/debates/{debate_id}")
async def get_debate(debate_id: str):
    """GET /api/v1/debates/{debate_id} → 200 OK / 404 Not Found"""
    debate = _debates.get(debate_id)
    if debate is None:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})
    return JSONResponse(status_code=200, content=debate)


@app.post("/api/v1/debates/{debate_id}/arguments")
async def create_argument(debate_id: str, request: Request):
    """POST /api/v1/debates/{debate_id}/arguments → 201 Created / 404 Not Found / 422

    Schema note 19-20: debate existence is checked BEFORE body validation.
    If debate_id is missing and body is also invalid, the response is 404.
    """
    if debate_id not in _debates:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=422, content={"error": "Invalid JSON body"})

    try:
        payload = ArgumentCreate.model_validate(body)
    except ValidationError as exc:
        return JSONResponse(status_code=422, content={"error": _first_error_msg(exc)})

    arg_id = str(uuid.uuid4())
    argument = {
        "id": arg_id,
        "debate_id": debate_id,  # always from path, never from request body
        "side": payload.side,
        "body": payload.body,
        "created_at": _now_utc(),
    }
    _arguments[arg_id] = argument
    return JSONResponse(status_code=201, content=argument)


@app.get("/api/v1/debates/{debate_id}/arguments")
async def list_arguments(
    debate_id: str,
    side: Optional[str] = Query(default=None),
):
    """GET /api/v1/debates/{debate_id}/arguments → 200 OK / 404 Not Found / 422

    Schema note 17: ?side= is validated BEFORE checking debate existence.
    An invalid side value returns 422 even if the debate does not exist.
    Other unrecognised query parameters are silently ignored (schema note 18).
    """
    if side is not None and side not in ("for", "against"):
        return JSONResponse(
            status_code=422,
            content={"error": "side must be 'for' or 'against'"},
        )

    if debate_id not in _debates:
        return JSONResponse(status_code=404, content={"error": "Debate not found"})

    result = [
        arg for arg in _arguments.values()
        if arg["debate_id"] == debate_id
        and (side is None or arg["side"] == side)
    ]
    result.sort(key=lambda a: a["created_at"])
    return JSONResponse(status_code=200, content=result)
