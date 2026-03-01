# CTO State

Dynamic working memory. Updated by CTO each cycle.
Full decisions log: `cto/decisions.md` (newest first).

---

## Mandate

We are building a **bookmark manager REST API** in Python using FastAPI.

**Endpoints:**
- `GET /health` → `{"status": "ok"}`
- `POST /bookmarks` → create bookmark: `{url, title, tags: []}` — returns 201 with `{id, url, title, tags}`
- `GET /bookmarks` → list all bookmarks; supports `?tag=xxx` to filter by tag (exact match within tags list)
- `GET /bookmarks/{id}` → get one, 404 if not found
- `DELETE /bookmarks/{id}` → delete, return deleted bookmark, 404 if not found

**Quality bar — all must pass before accepting:**
1. URL validation: `url` field must be a valid http/https URL. Use Pydantic's `AnyHttpUrl`. Bare strings like `"not-a-url"` must be rejected with 422.
2. Tag filtering: `GET /bookmarks?tag=python` must return only bookmarks where `"python"` is in their `tags` list. No tag param = return all.
3. `requirements.txt` must exist in `product/` with pinned versions (e.g. `fastapi==0.x.x`).
4. `README.md` must exist in `product/` with a working curl example for every endpoint.
5. Server starts with: `uvicorn main:app --port 8000`

**Done means:** all 5 endpoints work, URL validation rejects bad input, tag filtering works, requirements.txt and README.md are present.

---

## Backlog

### Needs Human Input
<!-- Tasks or decisions blocked on human — describe exactly what's needed -->
*(none)*

### Planned
<!-- Priority order. Format: - [task-XXX] Description | P1/P2/P3 | deps: none -->
*(none)*

### Active
<!-- Format: - [task-XXX] Description | status | branch -->
*(none)*

### Done (recent)
<!-- Keep last ~10. Format: - [task-XXX] Description | accepted/discarded | YYYY-MM-DD -->
- [task-002] Bookmark Manager REST API (Python/FastAPI) | accepted | 2026-03-01
- [task-001] Node.js REST API (items CRUD) | accepted | 2026-03-01

---

## Recent Decisions
<!-- Top 20 only — one line each. Full log in cto/decisions.md -->
<!-- Format: [YYYY-MM-DDTHH:MM] task-XXX ACTION — reason -->
- [2026-03-01T15:00] task-002 ACCEPTED — all 5 endpoints correct, AnyHttpUrl validation, tag filtering, pinned requirements.txt, README with curl examples; mandate complete
- [2026-03-01T14:00] CTO CYCLE PASS — no review action; task-002 assigned, task agent not yet run
- [2026-03-01T13:00] task-002 ASSIGNED — implement Python/FastAPI bookmark manager (mandate not yet built)
- [2026-03-01T12:00] task-001 ACCEPTED — all 5 endpoints correct, clean 42-line implementation, no PR found so accepted via branch diff
- [2026-03-01T00:00] task-001 ASSIGNED — first task: bootstrap product context + implement full REST API (Express, in-memory)
