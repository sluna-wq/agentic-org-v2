# Debate Engine API — Specialist Evaluation

**Author:** Agent C — QA Engineer (Contract Testing Specialist)
**Topology:** SPECIALIST
**Subject:** Agent B's `api.py` vs Agent A's `schema.md`
**Date:** 2026-03-01

---

## Overview

This evaluation assesses Agent B's FastAPI implementation against Agent A's contract
specification across five research dimensions. For each dimension I state what the schema
requires, what the implementation does, and whether they match. A "Specialist Observations"
subsection follows each dimension with notes on implementation quality, edge cases, and
testing implications that go beyond a simple pass/fail verdict.

---

## Dimension 1 — Field Names

### Schema requires

Exact field names (no aliases, no camelCase):

- **Debate:** `id`, `title`, `description`, `argument_count`, `created_at`
- **Argument:** `id`, `debate_id`, `side`, `body`, `created_at`

Fields that are server-generated and must never be writable by clients:
`id`, `created_at`, `argument_count`, `debate_id` (on Argument).

### Implementation does

- `DebateOut` defines: `id`, `title`, `description`, `argument_count`, `created_at` ✓
- `ArgumentOut` defines: `id`, `debate_id`, `side`, `body`, `created_at` ✓
- `DebateCreate` (request model) exposes only `title` and `description` — no server-owned
  fields are writable ✓
- `ArgumentCreate` exposes only `side` and `body` ✓
- `debate_id` on Argument is always set from the URL path parameter, never from the
  request body ✓

### Result: **PASS**

### Specialist Observations

The implementation uses separate request and response models (`DebateCreate`/`DebateOut`,
`ArgumentCreate`/`ArgumentOut`). This is architecturally correct for contract enforcement:
the type boundary prevents any accidental field bleed between the writable and read-only
surfaces.

One subtle point worth flagging for tests: the schema specifies `description` must default
to `""` (empty string) when omitted by the client — not `null` or `None`. The Pydantic
`Field(default="", ...)` on `DebateCreate` implements this correctly, and `DebateOut.description`
is typed `str` (not `Optional[str]`), so `None` cannot appear in responses. Tests should
explicitly assert `body["description"] == ""` (string equality, not just truthiness) to
catch any regression where the field becomes nullable.

---

## Dimension 2 — Response Envelopes

### Schema requires

- `POST /api/v1/debates` → single `Debate` object (dict), **not** a list
- `GET /api/v1/debates` → `{"debates": [...], "total": N}` (named wrapper, not a bare array)
- `GET /api/v1/debates/{id}` → single `Debate` object (dict)
- `POST /api/v1/debates/{id}/arguments` → single `Argument` object (dict)
- `GET /api/v1/debates/{id}/arguments` → `{"arguments": [...], "total": N}`

`total` must equal the count of items in the returned list (after any `?side=` filtering).

### Implementation does

- `DebateOut` (Pydantic model) is returned for single-debate endpoints ✓
- `DebateListOut` defines `debates: list[DebateOut]` and `total: int` ✓
- `ArgumentOut` is returned for single-argument endpoints ✓
- `ArgumentListOut` defines `arguments: list[ArgumentOut]` and `total: int` ✓
- `total` in `DebateListOut` and `ArgumentListOut` is set to `len(sorted_debates)` and
  `len(result)` respectively ✓

### Result: **PASS**

### Specialist Observations

The envelope key names (`"debates"`, `"arguments"`) are plural and match the resource
name exactly as specified. Tests should assert both `isinstance(body, dict)` (envelope
is not a bare array) **and** the presence of both `"debates"`/`"arguments"` and `"total"`
keys using set equality rather than `in` checks, so that unexpected extra keys are caught.

The `total` in `ArgumentListOut` is derived from `len(result)` where `result` is the
already-filtered list. This means `total` will correctly reflect the filtered count when
`?side=` is active, which matches the schema requirement. A common implementation mistake
is to set `total` to the unfiltered count; the implementation avoids this.

---

## Dimension 3 — Status Codes

### Schema requires

| Endpoint | Success | Error conditions |
|---|---|---|
| `POST /api/v1/debates` | 201 | 422 |
| `GET /api/v1/debates` | 200 | — |
| `GET /api/v1/debates/{id}` | 200 | 404 |
| `POST /api/v1/debates/{id}/arguments` | 201 | 404, 422 |
| `GET /api/v1/debates/{id}/arguments` | 200 | 404, 422 |

### Implementation does

- `@app.post(..., status_code=201)` on both POST endpoints ✓
- `@app.get(..., status_code=200)` on all GET endpoints ✓
- `HTTPException(status_code=404, ...)` raised for missing debates ✓
- Pydantic `Literal` constraint on `side` (both body and query) causes FastAPI to emit 422
  for invalid values ✓

### Result: **PASS**

### Specialist Observations

The implementation registers status codes declaratively on the route decorator rather than
constructing `JSONResponse(status_code=...)` by hand. This means the framework enforces
the code — a regression would require actively overriding the decorator, which is unlikely.

One noteworthy edge case: `GET /api/v1/debates/{debate_id}/arguments?side=<invalid>` will
return **422** even if `debate_id` does not exist, because FastAPI validates query parameters
before executing the handler body. This means an invalid `?side=` value can mask a 404. The
schema is silent on this ordering; it specifies both conditions independently but does not
define a precedence rule. The implementation's behavior (422 wins over 404) is a reasonable
interpretation and is consistent with framework-first validation, but it is worth documenting
for consumers: clients cannot rely on a 404 being returned for a nonexistent debate when they
also supply an invalid `side` query parameter.

---

## Dimension 4 — `?side=` Filter

### Schema requires

| Input | Expected behavior |
|---|---|
| `?side=` omitted | Return all arguments for the debate |
| `?side=for` | Return only arguments where `side == "for"` |
| `?side=against` | Return only arguments where `side == "against"` |
| Any other value | 422 (case-sensitive; `"For"`, `"FOR"`, `"pro"`, `"yes"` are all invalid) |

`total` in the response must reflect the filtered count.

### Implementation does

```python
side: Optional[Literal["for", "against"]] = Query(default=None)
```

- `None` (omitted) → `side is None or a["side"] == side` evaluates to `True` for all ✓
- `"for"` → only `"for"` arguments pass the filter ✓
- `"against"` → only `"against"` arguments pass the filter ✓
- Any other value → Pydantic `Literal` constraint triggers 422 ✓
- Case-sensitive enforcement: `Literal["for", "against"]` rejects `"For"`, `"FOR"`,
  `"Against"`, `"pro"` automatically ✓
- `total` = `len(result)` where `result` is already filtered ✓

### Result: **PASS**

### Specialist Observations

Using `Literal["for", "against"]` as the query param type is an elegant and robust approach.
The constraint is declared once, enforced by Pydantic, reflected in the OpenAPI schema, and
requires no custom validation code. This eliminates an entire class of implementation bugs
where a hand-written validator might accept `"For"` due to a case-insensitive comparison.

The validation is applied by Pydantic before the handler body runs, which means the 422 is
returned **before** the debate-existence check (as noted in Dimension 3). Tests for the
filter should cover: (a) the happy path for both values, (b) case variants of valid values
(`"For"`, `"FOR"`, `"Against"`), (c) plausible-but-wrong values (`"pro"`, `"con"`, `"yes"`,
`"neutral"`), and (d) an empty string `?side=`. All should return 422.

---

## Dimension 5 — 422 Error Envelope

### Schema requires

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

The schema explicitly states: *"FastAPI validation errors (422) use FastAPI's native format."*
This is distinct from application-level errors (404) which use `{"error": "string"}`.

### Implementation does

The implementation registers a custom `RequestValidationError` exception handler:

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    msg = "Validation error"
    if errors:
        raw = errors[0].get("msg", msg)
        msg = raw.removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"error": msg})
```

This overrides FastAPI's native 422 response shape and returns `{"error": "..."}` instead
of `{"detail": [...]}`.

**The implementation returns for a missing `title`:**
```json
{"error": "Field required"}
```

**The schema requires:**
```json
{
  "detail": [
    {"loc": ["body", "title"], "msg": "Field required", "type": "missing"}
  ]
}
```

### Result: **FAIL** — Contract violation

### Specialist Observations

This is the most significant contract deviation in the implementation. The schema draws an
explicit architectural distinction between two error classes:

1. **Application errors** (404 Not Found): `{"error": "..."}` — a human-readable string
2. **Validation errors** (422 Unprocessable Entity): FastAPI native `{"detail": [...]}` —
   a machine-parseable list of structured error objects

The implementation collapses both into the same `{"error": "..."}` envelope. This has
concrete consequences for API consumers:

- Clients that parse 422 `detail` arrays to show per-field validation messages will break
- Clients cannot distinguish a 404 from a 422 by envelope shape alone — only by status code
- The structured location information (`loc`) that tells clients *which* field failed
  validation is discarded
- The schema's `"type"` field (e.g., `"value_error.missing"`, `"string_too_short"`) that
  enables programmatic error handling is lost

**Additional note on schema precision:** The schema shows `"type": "value_error.missing"`,
which is Pydantic v1 error format. The implementation uses Pydantic v2 (via FastAPI ≥ 0.100),
which would produce `"type": "missing"` (without the `"value_error."` prefix). If the
implementation were to revert to FastAPI's native 422 handler, the `"type"` values in the
errors would differ from the schema's example. Tests should check structural shape (presence
of `"detail"` as a list with `"loc"` and `"msg"` keys) rather than exact `"type"` string
values, to avoid Pydantic version brittleness.

---

## Score: 4/5

| Dimension | Result |
|---|---|
| 1. Field names | ✓ PASS |
| 2. Response envelopes | ✓ PASS |
| 3. Status codes | ✓ PASS |
| 4. `?side=` filter | ✓ PASS |
| 5. 422 error envelope | ✗ FAIL |

---

## Specialist Verdict

Agent B's implementation demonstrates strong contract discipline across four of five
dimensions. The field naming is exact, the response envelopes are correctly structured,
the status codes are accurately assigned, and the `?side=` filter is robustly implemented
using Pydantic's `Literal` type rather than a hand-written validator. The use of dynamic
`argument_count` computation (derived on read rather than stored as a mutable counter)
is a sound engineering decision that eliminates a whole class of consistency bugs at the
cost of an O(N) scan over `_arguments` per debate — negligible for in-memory storage but
worth flagging for a future persistence layer. The separation of request and response
Pydantic models is architecturally correct and creates a clean, verifiable contract
boundary at the type level.

The single contract violation is the custom `RequestValidationError` handler that overrides
FastAPI's native 422 envelope with `{"error": "..."}`. The schema is unambiguous here: it
explicitly distinguishes the 422 envelope from the 404 envelope and specifies FastAPI's
native `{"detail": [...]}` format for validation errors. This deviation would break any API
consumer that implements structured validation-error handling per the contract. It is the
only change required to bring the implementation into full compliance: remove the custom
`validation_exception_handler`. The fix is trivially small; the violation's impact on
consumer correctness is not.
