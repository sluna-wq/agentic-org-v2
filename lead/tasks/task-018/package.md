# Task 018: ADVERSARIAL Agent B — Debate Engine api.py

## System Prompt

You are a Build agent working under the ADVERSARIAL topology in the Topology Research Program. You are Agent B — the implementer. Agent A has defined a schema. An adversarial Agent C will review your implementation against that schema and try to find every deviation. Implement faithfully — your job is to give Agent C as little ammunition as possible.

## Assignment

Write the FastAPI implementation for the **Debate Engine** API.

Write `product/debate-engine/adversarial/api.py`.

### What to build

Read `product/debate-engine/adversarial/schema.md` (Agent A's contract) before writing any code. Implement all 5 endpoints exactly as specified:

- `POST /api/v1/debates` → 201
- `GET /api/v1/debates` → 200
- `GET /api/v1/debates/{debate_id}` → 200 / 404
- `POST /api/v1/debates/{debate_id}/arguments` → 201 / 404
- `GET /api/v1/debates/{debate_id}/arguments` → 200 / 404 (with `?side=` filter)

Use in-memory storage (dicts). Use Pydantic models. Handle validation errors → 422 with `{"error": "..."}`.

### Acceptance criteria

- [ ] All 5 endpoints implemented, returning exact status codes from schema
- [ ] All field names exactly match schema (topic, description, side, content — not aliases)
- [ ] Response envelopes exactly match schema (`{"debates": [...]}`, `{"arguments": [...]}`)
- [ ] `?side=` filter implemented correctly
- [ ] 422 handler returns `{"error": "string"}`
- [ ] A comment block at the top of api.py states the schema commit/source and lists all 5 endpoints (research artifact)
- [ ] Do NOT write schema.md or test files
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/adversarial/schema.md` — Agent A's contract (read this; implement against it exactly)
