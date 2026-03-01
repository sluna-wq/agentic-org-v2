# Task 016: PIPELINE Agent C — Debate Engine tests/test_api.py

## System Prompt

You are a Build agent working under the PIPELINE topology in the Topology Research Program. You are Agent C — the final link in the pipeline. Agents A and B have already produced a schema.md and api.py. You have full access to both. Write tests that verify the implementation matches the schema.

## Assignment

Write pytest tests for the **Debate Engine** FastAPI API.

Write `product/debate-engine/pipeline/tests/test_api.py`.
Also write `product/debate-engine/pipeline/tests/__init__.py` (empty file).
Also write `product/debate-engine/pipeline/tests/conftest.py` — import the real app from `product/debate-engine/pipeline/api.py`.

### What to build

Read `product/debate-engine/pipeline/schema.md` and `product/debate-engine/pipeline/api.py` before writing tests. Your tests must verify that the implementation conforms to the schema.

Minimum test coverage required:
- Create a debate → 201 + response body shape
- List debates → 200 + list structure
- Get a single debate by ID → 200
- Get a non-existent debate by ID → 404
- Add an argument to a debate → 201 + response body shape
- List arguments for a debate → 200 + list structure

### Acceptance criteria

- [ ] Uses pytest + `starlette.testclient.TestClient` or `httpx.AsyncClient`
- [ ] conftest.py imports the real app from `product/debate-engine/pipeline/api.py`
- [ ] At the top of `test_api.py`, a comment block documents the API contract your tests assume (copied/confirmed from schema.md) — this is the research measurement artifact
- [ ] All 6 coverage areas have at least one test each
- [ ] Do NOT write api.py or ui.html
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/pipeline/schema.md` — Agent A's contract (read this)
- `product/debate-engine/pipeline/api.py` — Agent B's implementation (read this; import app from here)
