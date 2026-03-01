from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Debate Engine")

# In-memory storage
debates: dict[str, dict] = {}
arguments: dict[str, list[dict]] = {}


# --- Pydantic models ---

class DebateCreate(BaseModel):
    topic: str
    description: str


class Debate(BaseModel):
    id: str
    topic: str
    description: str
    created_at: str


class ArgumentCreate(BaseModel):
    side: Literal["for", "against"]
    content: str


class Argument(BaseModel):
    id: str
    debate_id: str
    side: Literal["for", "against"]
    content: str
    created_at: str


# --- Endpoints ---

@app.post("/debates", response_model=Debate, status_code=201)
def create_debate(body: DebateCreate) -> Debate:
    debate_id = str(uuid4())
    debate = {
        "id": debate_id,
        "topic": body.topic,
        "description": body.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    debates[debate_id] = debate
    arguments[debate_id] = []
    return Debate(**debate)


@app.get("/debates", response_model=list[Debate], status_code=200)
def list_debates() -> list[Debate]:
    return [Debate(**d) for d in debates.values()]


@app.get("/debates/{debate_id}", response_model=Debate, status_code=200)
def get_debate(debate_id: str) -> Debate:
    debate = debates.get(debate_id)
    if debate is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    return Debate(**debate)


@app.post("/debates/{debate_id}/arguments", response_model=Argument, status_code=201)
def add_argument(debate_id: str, body: ArgumentCreate) -> Argument:
    if debate_id not in debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    arg = {
        "id": str(uuid4()),
        "debate_id": debate_id,
        "side": body.side,
        "content": body.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    arguments[debate_id].append(arg)
    return Argument(**arg)


@app.get("/debates/{debate_id}/arguments", response_model=list[Argument], status_code=200)
def list_arguments(debate_id: str) -> list[Argument]:
    if debate_id not in debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    return [Argument(**a) for a in arguments[debate_id]]
