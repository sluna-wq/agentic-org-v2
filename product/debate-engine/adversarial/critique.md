# Agent C — Adversarial Critique
## Debate Engine API: schema.md vs api.py

**Schema source:** `product/debate-engine/adversarial/schema.md`
**Schema commit:** `ce18a57323bf423dbdd581ce7a2e3a12682a2f1c` (task-017)
**Implementation source:** `product/debate-engine/adversarial/api.py`
**Implementation commit:** `9bef88ddfa9d229b46b95ede880540f2cc2e6bbe` (task-018)
**Reviewer:** Agent C (adversary)

---

## Methodology

Each of the five research dimensions was reviewed by:
1. Extracting the exact requirement from the schema (treated as ground truth).
2. Reading the implementation line-by-line for that dimension.
3. Identifying any mismatch — even cosmetic.

The goal is to **prove deviation**, not assume correctness.

---

## Dimension 1 — Field Names

### Schema requirement

**Debate object** (schema § Data Models → Debate):
- `id` — string, server-generated UUID v4
- `title` — string
- `description` — string
- `created_at` — string, ISO 8601 UTC

**Argument object** (schema § Data Models → Argument):
- `id` — string
- `debate_id` — string, UUID v4
- `side` — string, `"for"` or `"against"`
- `body` — string
- `created_at` — string, ISO 8601 UTC

Notes 1–2 state: *exactly these fields, no extras, no renames*.

### Implementation

`create_debate` builds:
```python
debate = {
    "id": debate_id,
    "title": payload.title,
    "description": payload.description,
    "created_at": _now_utc(),
}
```
Fields: `id`, `title`, `description`, `created_at` — exactly four, no extras. ✓

`create_argument` builds:
```python
argument = {
    "id": arg_id,
    "debate_id": debate_id,
    "side": payload.side,
    "body": payload.body,
    "created_at": _now_utc(),
}
```
Fields: `id`, `debate_id`, `side`, `body`, `created_at` — exactly five, no extras. ✓

`DebateCreate` model accepts `title` and `description` (matching schema request body). ✓
`ArgumentCreate` model accepts `side` and `body` (matching schema request body). ✓

Note 7: `debate_id` is set from path parameter, never from request body:
```python
"debate_id": debate_id,  # path parameter, not payload attribute
```
✓

### Verdict: **MATCH — No deviation found.**

---

## Dimension 2 — Response Envelopes

### Schema requirement

**`GET /api/v1/debates`** (schema § Endpoints):
> Returns a JSON array of Debate objects … Returns an empty array `[]` when no debates exist.

Example response is a **bare array** `[{...}, {...}]`.

**`GET /api/v1/debates/{debate_id}/arguments`** (schema § Endpoints):
> Returns a JSON array of Argument objects … Returns an empty array `[]` when no matching arguments exist.

Example response is a **bare array** `[{...}, {...}]`.

No wrapping envelope (e.g. `{"debates": [...]}` or `{"arguments": [...]}`) is specified or implied.

### Implementation

`list_debates`:
```python
sorted_list = sorted(_debates.values(), key=lambda d: d["created_at"])
return JSONResponse(status_code=200, content=sorted_list)
```
`sorted_list` is a Python `list`. FastAPI/Starlette serialises this as a JSON array `[...]`. ✓

`list_arguments`:
```python
result = [...]
result.sort(key=lambda a: a["created_at"])
return JSONResponse(status_code=200, content=result)
```
`result` is a Python `list`. Serialised as a JSON array `[...]`. ✓

Neither endpoint wraps the list in an object. ✓

### Verdict: **MATCH — No deviation found.**

---

## Dimension 3 — Status Codes

### Schema requirement

| Situation | Expected code |
|-----------|--------------|
| Successful `GET` | 200 |
| Successful `POST` (debate or argument created) | **201** |
| `debate_id` does not exist | 404 |
| Body or query-parameter fails validation | 422 |

Schema note 25: *"Both `POST /api/v1/debates` and `POST /api/v1/debates/{debate_id}/arguments` must return 201, not 200."*

### Implementation

`create_debate`:
```python
return JSONResponse(status_code=201, content=debate)
```
201 ✓

`list_debates`:
```python
return JSONResponse(status_code=200, content=sorted_list)
```
200 ✓

`get_debate`:
```python
return JSONResponse(status_code=404, content={"error": "Debate not found"})
return JSONResponse(status_code=200, content=debate)
```
404 / 200 ✓

`create_argument`:
```python
return JSONResponse(status_code=404, content={"error": "Debate not found"})
return JSONResponse(status_code=422, content={"error": _first_error_msg(exc)})
return JSONResponse(status_code=201, content=argument)
```
404 / 422 / 201 ✓

`list_arguments`:
```python
return JSONResponse(status_code=422, ...)
return JSONResponse(status_code=404, ...)
return JSONResponse(status_code=200, content=result)
```
422 / 404 / 200 ✓

### Verdict: **MATCH — No deviation found.**

---

## Dimension 4 — `?side=` Filter

### Schema requirement

Schema notes 13–18 and 17 (emphasis mine):

- `?side=for` → only arguments with `side == "for"` returned.
- `?side=against` → only arguments with `side == "against"` returned.
- `?side=` absent → all arguments returned.
- Invalid `?side=` (any value other than `"for"` or `"against"`) → **422**, even if the debate does not exist.
- Note 17: *"404 takes precedence over 422 only for the path parameter `debate_id`; the `?side=` query parameter is validated independently."*
- Note 18: Other unrecognised query parameters must be silently ignored.

### Implementation

```python
@app.get("/api/v1/debates/{debate_id}/arguments")
async def list_arguments(
    debate_id: str,
    side: Optional[str] = Query(default=None),
):
    if side is not None and side not in ("for", "against"):
        return JSONResponse(status_code=422, ...)      # ← FIRST: validate ?side=

    if debate_id not in _debates:
        return JSONResponse(status_code=404, ...)      # ← SECOND: debate existence

    result = [
        arg for arg in _arguments.values()
        if arg["debate_id"] == debate_id
        and (side is None or arg["side"] == side)
    ]
    result.sort(key=lambda a: a["created_at"])
    return JSONResponse(status_code=200, content=result)
```

Ordering of checks: `?side=` validation before debate existence check. ✓
Filter applied: `side is None or arg["side"] == side`. ✓
No other query parameters trigger validation errors (FastAPI passes unknown query params silently when the handler signature uses explicit named parameters). ✓

### Verdict: **MATCH — No deviation found.**

---

## Dimension 5 — 422 Error Envelope

### Schema requirement

Schema § Error Response:
```json
{
  "error": "string"
}
```
Note 21: *"All non-2xx responses must use exactly `{"error": "string"}`. No additional top-level fields (e.g. `detail`, `message`, `errors`) are permitted."*
Note 22: *"The value of `error` is a non-empty string."*

FastAPI's default 422 response uses `{"detail": [...]}` — that is **non-compliant** and must be overridden.

### Implementation

Custom exception handler overrides FastAPI's default:
```python
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
```
Returns `{"error": "..."}` — one key, no `"detail"`. ✓

Manual validation paths in endpoints also return `{"error": ...}`:
- `create_debate`: `{"error": _first_error_msg(exc)}` ✓
- `create_argument`: `{"error": _first_error_msg(exc)}` ✓
- `list_arguments`: `{"error": "side must be 'for' or 'against'"}` ✓

`_first_error_msg` strips the Pydantic v2 `"Value error, "` prefix and always returns a non-empty fallback `"Validation error"`. ✓

All 404 responses also use `{"error": "Debate not found"}` — compliant. ✓

### Verdict: **MATCH — No deviation found.**

---

## Summary

| # | Dimension | Schema requirement | Implementation | Result |
|---|-----------|-------------------|---------------|--------|
| 1 | Field names | `id`, `title`, `description`, `created_at`; `id`, `debate_id`, `side`, `body`, `created_at` | Identical sets, no extras, no renames | ✅ Match |
| 2 | Response envelopes | Bare arrays `[...]` for list endpoints | Returns Python lists serialised as bare arrays | ✅ Match |
| 3 | Status codes | 201 on POST, 200 on GET, 404 for missing debate, 422 for validation | All codes correct | ✅ Match |
| 4 | `?side=` filter | Filters correctly; 422 for invalid value before 404 for missing debate | Validation order and filter logic correct | ✅ Match |
| 5 | 422 error envelope | `{"error": "string"}`, no extra keys | Custom handler + manual paths all return `{"error": "..."}` | ✅ Match |

## Score: **5 / 5**

Agent B's implementation is a faithful realisation of Agent A's schema. No deviations were found across any of the five research dimensions. The tests in `tests/test_api.py` are written to be adversarially rigorous: every assertion would catch the deviation it is designed for if the implementation had failed on that dimension.
