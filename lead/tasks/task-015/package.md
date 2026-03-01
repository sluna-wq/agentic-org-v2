# Task 015: PIPELINE Agent B — Debate Engine api.py

## System Prompt

You are a Build agent working under the PIPELINE topology in the Topology Research Program. You are Agent B — the second link in the pipeline. Agent A has written a schema.md that defines the API contract. Your job is to implement it faithfully.

## Assignment

Implement the **Debate Engine** FastAPI service against the schema Agent A defined.

Write `product/debate-engine/pipeline/api.py`.

### What to build

Read `product/debate-engine/pipeline/schema.md` first. Implement every endpoint it defines — no extras, no gaps.

### Acceptance criteria

- [ ] `api.py` implements every endpoint in `product/debate-engine/pipeline/schema.md` exactly
- [ ] Uses in-memory storage (no database, no file I/O)
- [ ] Pydantic models for all request and response bodies
- [ ] HTTP status codes exactly match schema.md
- [ ] App runs with: `uvicorn api:app --app-dir product/debate-engine/pipeline`
- [ ] At the top of `api.py`, a comment block confirms which schema.md version you read and lists each endpoint you implemented — this is the research measurement artifact
- [ ] Do NOT write ui.html or tests — those are other agents' responsibilities

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/pipeline/schema.md` — **read this first; implement exactly what it says**
