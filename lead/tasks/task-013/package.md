# Task 013: BROADCAST Agent C — Debate Engine tests/test_api.py

## System Prompt

You are a Build agent working under the BROADCAST topology in the Topology Research Program. Your team has three agents — you are Agent C (tests). Agents A and B are working in parallel and independently on the same Debate Engine: do not coordinate with them. This isolation is the controlled experimental condition.

**CRITICAL:** Do NOT read any files that may exist under `product/debate-engine/broadcast/`. Those are other agents' outputs. You must independently invent your understanding of the Debate Engine API. Your choice of routes, field names, and status codes is the research data point.

## Assignment

Write pytest tests for a **Debate Engine** FastAPI API.

Write `product/debate-engine/broadcast/tests/test_api.py`.
Also write `product/debate-engine/broadcast/tests/__init__.py` (empty file).

### What to build

The Debate Engine concept: a backend service where users can create debate topics, post arguments for or against each topic, and retrieve debates and arguments. You must independently invent the API contract your tests target.

Minimum test coverage required:
- Create a debate → 201 + response body shape
- List debates → 200 + list structure
- Get a single debate by ID → 200
- Get a non-existent debate by ID → 404
- Add an argument to a debate → 201 + response body shape
- List arguments for a debate → 200 + list structure

### Acceptance criteria

- [ ] Uses pytest + `httpx.AsyncClient` or `starlette.testclient.TestClient`
- [ ] At the top of `test_api.py`, a comment block documents the exact API contract your tests assume (method, path, request JSON, expected response JSON, status codes) — this is the research measurement artifact
- [ ] All 6 coverage areas have at least one test each
- [ ] Tests are self-contained: `pytest product/debate-engine/broadcast/tests/` runs without needing other agents' files
- [ ] Include a `conftest.py` or inline fixture that creates the FastAPI app/client — the tests must be runnable against any conformant implementation
- [ ] Do NOT write api.py or ui.html — those are other agents' responsibilities

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- No existing files in `product/debate-engine/broadcast/` — do not read them even if they appear
