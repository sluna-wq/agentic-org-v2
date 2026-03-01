# Task 002: Bookmark Manager REST API (Python/FastAPI)

## System Prompt
You are a Python backend engineer. You write clean, minimal FastAPI code. You do not over-engineer. You follow the product CLAUDE.md before writing any code.

## Assignment

Implement a bookmark manager REST API in Python using FastAPI with in-memory storage.

### Endpoints (all required):
1. `GET /health` → `{"status": "ok"}`
2. `POST /bookmarks` → create a bookmark; body: `{url, title, tags: []}` → 201 with `{id, url, title, tags}`
3. `GET /bookmarks` → list all; supports `?tag=xxx` to filter by tag (exact match within tags list); no tag param = return all
4. `GET /bookmarks/{id}` → get one; 404 if not found
5. `DELETE /bookmarks/{id}` → delete; return deleted bookmark; 404 if not found

### Acceptance criteria (all must pass):
1. **URL validation**: `url` field must be a valid http/https URL using Pydantic's `AnyHttpUrl`. A bare string like `"not-a-url"` must be rejected with 422.
2. **Tag filtering**: `GET /bookmarks?tag=python` returns only bookmarks where `"python"` is in their `tags` list.
3. **`requirements.txt`** in `product/` with pinned versions (e.g. `fastapi==0.x.x`, `uvicorn==0.x.x`).
4. **`README.md`** in `product/` with a working `curl` example for every endpoint.
5. **Server starts** with: `uvicorn main:app --port 8000`
6. **Update `product/CLAUDE.md`** with accurate project layout and how to run the server.

### Files to create:
- `product/main.py` — FastAPI app, all 5 endpoints
- `product/requirements.txt` — pinned deps
- `product/README.md` — curl examples for all 5 endpoints

## Relevant Files
- `product/CLAUDE.md` — read before writing any code
