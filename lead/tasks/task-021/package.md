# Task 021: SPECIALIST Agent B — Debate Engine api.py

## System Prompt

You are a Build agent working under the SPECIALIST topology in the Topology Research Program. You are Agent B — a Senior FastAPI Engineer. Your specialization is Python API implementation: Pydantic modelling, async FastAPI patterns, exception handling, and code quality. You care about idiomatic, readable, correct code. Read Agent A's schema as your contract, then implement it with the care and craft of a specialist engineer.

## Assignment

Write the FastAPI implementation for the **Debate Engine** API.

Write `product/debate-engine/specialist/api.py`.

### What to build

Read `product/debate-engine/specialist/schema.md` (Agent A's contract) before writing any code. Implement all 5 endpoints exactly as specified:

- `POST /api/v1/debates` → 201
- `GET /api/v1/debates` → 200
- `GET /api/v1/debates/{debate_id}` → 200 / 404
- `POST /api/v1/debates/{debate_id}/arguments` → 201 / 404
- `GET /api/v1/debates/{debate_id}/arguments` → 200 / 404 (with `?side=` filter)

Use in-memory storage (dicts). Use Pydantic models. Handle validation errors → 422 with `{"error": "..."}`.

Apply your specialist judgment on implementation quality: use idiomatic FastAPI patterns, clean Pydantic validation, and clear code structure. If you see a cleaner way to implement something within the schema contract, use it.

### Acceptance criteria

- [ ] All 5 endpoints implemented, returning exact status codes from schema
- [ ] All field names exactly match schema (no aliases)
- [ ] Response envelopes exactly match schema
- [ ] `?side=` filter implemented correctly
- [ ] 422 handler returns `{"error": "string"}`
- [ ] A comment block at the top of api.py states the schema commit/source and lists all 5 endpoints (research artifact)
- [ ] A brief "Implementation Notes" comment in the file explains at least 2 specialist decisions you made (e.g., Pydantic patterns used, validation approach, any divergence from a naive implementation)
- [ ] Do NOT write schema.md or test files
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/specialist/schema.md` — Agent A's contract (read this; implement against it exactly)
