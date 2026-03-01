# Debate Engine API — Contract Specification

**Author:** Agent A — Senior REST API Designer
**Topology:** SPECIALIST
**Version:** v1
**Base URL:** `/api/v1`

---

## Data Models

### Debate

| Field            | Type    | Source         | Constraints                    |
|------------------|---------|----------------|--------------------------------|
| `id`             | string  | server         | UUID v4; read-only             |
| `title`          | string  | client         | Required; 1–200 characters     |
| `description`    | string  | client         | Optional; 0–1000 characters; defaults to `""` |
| `argument_count` | integer | server         | Read-only; non-negative; maintained by server |
| `created_at`     | string  | server         | ISO 8601 UTC; e.g. `"2026-03-01T12:00:00Z"`; read-only |

**Example:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Renewable energy should replace fossil fuels within 20 years",
  "description": "Focus on economic and environmental feasibility.",
  "argument_count": 4,
  "created_at": "2026-03-01T09:00:00Z"
}
```

---

### Argument

| Field       | Type   | Source | Constraints                                     |
|-------------|--------|--------|-------------------------------------------------|
| `id`        | string | server | UUID v4; read-only                              |
| `debate_id` | string | server | UUID v4; matches the parent debate; read-only   |
| `side`      | string | client | Required; one of `"for"` or `"against"` exactly |
| `body`      | string | client | Required; 1–2000 characters                     |
| `created_at`| string | server | ISO 8601 UTC; read-only                         |

**Example:**
```json
{
  "id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "debate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "side": "for",
  "body": "Solar and wind costs have dropped over 90% in the last decade, making the transition economically viable.",
  "created_at": "2026-03-01T09:15:00Z"
}
```

---

## Error Response Shape

All application-level errors (404, etc.) use this shape:

```json
{ "error": "string" }
```

FastAPI validation errors (422) use FastAPI's native format:

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

---

## Endpoints

---

### `POST /api/v1/debates`

Create a new debate topic.

**Request body:**
```json
{
  "title": "Renewable energy should replace fossil fuels within 20 years",
  "description": "Focus on economic and environmental feasibility."
}
```

| Field         | Required | Type   | Constraints        |
|---------------|----------|--------|--------------------|
| `title`       | yes      | string | 1–200 characters   |
| `description` | no       | string | 0–1000 characters; defaults to `""` |

**Response `201 Created`:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Renewable energy should replace fossil fuels within 20 years",
  "description": "Focus on economic and environmental feasibility.",
  "argument_count": 0,
  "created_at": "2026-03-01T09:00:00Z"
}
```

**Response `422 Unprocessable Entity`** — missing or invalid fields (FastAPI validation format).

---

### `GET /api/v1/debates`

List all debates. Ordered by `created_at` descending (newest first).

**Request body:** none
**Query parameters:** none

**Response `200 OK`:**
```json
{
  "debates": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Renewable energy should replace fossil fuels within 20 years",
      "description": "Focus on economic and environmental feasibility.",
      "argument_count": 4,
      "created_at": "2026-03-01T09:00:00Z"
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "title": "Remote work improves productivity",
      "description": "",
      "argument_count": 1,
      "created_at": "2026-02-28T14:30:00Z"
    }
  ],
  "total": 2
}
```

---

### `GET /api/v1/debates/{debate_id}`

Get a single debate by ID.

**Path parameters:**

| Parameter   | Type   | Description      |
|-------------|--------|------------------|
| `debate_id` | string | UUID of the debate |

**Response `200 OK`:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Renewable energy should replace fossil fuels within 20 years",
  "description": "Focus on economic and environmental feasibility.",
  "argument_count": 4,
  "created_at": "2026-03-01T09:00:00Z"
}
```

**Response `404 Not Found`:**
```json
{ "error": "Debate not found" }
```

---

### `POST /api/v1/debates/{debate_id}/arguments`

Add an argument to a debate.

**Path parameters:**

| Parameter   | Type   | Description        |
|-------------|--------|--------------------|
| `debate_id` | string | UUID of the debate |

**Request body:**
```json
{
  "side": "for",
  "body": "Solar and wind costs have dropped over 90% in the last decade, making the transition economically viable."
}
```

| Field  | Required | Type   | Constraints                         |
|--------|----------|--------|-------------------------------------|
| `side` | yes      | string | Must be exactly `"for"` or `"against"` |
| `body` | yes      | string | 1–2000 characters                   |

**Response `201 Created`:**
```json
{
  "id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "debate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "side": "for",
  "body": "Solar and wind costs have dropped over 90% in the last decade, making the transition economically viable.",
  "created_at": "2026-03-01T09:15:00Z"
}
```

**Response `404 Not Found`:**
```json
{ "error": "Debate not found" }
```

**Response `422 Unprocessable Entity`** — missing or invalid fields (FastAPI validation format).

---

### `GET /api/v1/debates/{debate_id}/arguments`

List arguments for a debate. Optionally filter by side.

Ordered by `created_at` ascending (oldest first — chronological debate flow).

**Path parameters:**

| Parameter   | Type   | Description        |
|-------------|--------|--------------------|
| `debate_id` | string | UUID of the debate |

**Query parameters:**

| Parameter | Required | Type   | Constraints                                     |
|-----------|----------|--------|-------------------------------------------------|
| `side`    | no       | string | If provided, must be `"for"` or `"against"` exactly; omit to return all arguments |

**Response `200 OK`** (no filter):
```json
{
  "arguments": [
    {
      "id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
      "debate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "side": "for",
      "body": "Solar and wind costs have dropped over 90% in the last decade, making the transition economically viable.",
      "created_at": "2026-03-01T09:15:00Z"
    },
    {
      "id": "e8d7c6b5-a4f3-2109-edcb-a98765432109",
      "debate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "side": "against",
      "body": "The grid infrastructure required for full renewable transition does not yet exist at scale.",
      "created_at": "2026-03-01T09:22:00Z"
    }
  ],
  "total": 2
}
```

**Response `200 OK`** (`?side=for`):
```json
{
  "arguments": [
    {
      "id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
      "debate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "side": "for",
      "body": "Solar and wind costs have dropped over 90% in the last decade, making the transition economically viable.",
      "created_at": "2026-03-01T09:15:00Z"
    }
  ],
  "total": 1
}
```

**Response `404 Not Found`:**
```json
{ "error": "Debate not found" }
```

**Response `422 Unprocessable Entity`** — if `side` query param is present but not `"for"` or `"against"`.

---

## Notes for Agent B

These are the constraints you must implement exactly. No deviations.

### Field names

Use these exact field names — no aliases, no camelCase variants:

- Debate: `id`, `title`, `description`, `argument_count`, `created_at`
- Argument: `id`, `debate_id`, `side`, `body`, `created_at`

### Server-generated fields — never accept from client

The following fields are server-set and must be **ignored if submitted by a client** (do not expose them as writable):

- `id` — generate UUID v4 on the server
- `created_at` — set to current UTC time on creation
- `argument_count` — compute/maintain on the server; increment by 1 each time an argument is added to a debate
- `debate_id` on Argument — set to the `{debate_id}` path parameter, not from request body

### Allowed values for `side`

- Accept exactly: `"for"`, `"against"`
- Case-sensitive: `"For"`, `"FOR"`, `"Against"` are **invalid** and must return 422
- No other values permitted

### String length constraints

| Field              | Min | Max  |
|--------------------|-----|------|
| `title`            | 1   | 200  |
| `description`      | 0   | 1000 |
| `body` (Argument)  | 1   | 2000 |

- Empty string `""` is invalid for `title` and `body` (min 1)
- `description` defaults to `""` when omitted — do not treat as null/None in responses

### Ordering rules

- `GET /api/v1/debates` — debates ordered by `created_at` **descending** (newest first)
- `GET /api/v1/debates/{debate_id}/arguments` — arguments ordered by `created_at` **ascending** (oldest first)

### Filter behavior for `?side=`

- Omitted → return all arguments for the debate
- `?side=for` → return only `"for"` arguments
- `?side=against` → return only `"against"` arguments
- Any other value (e.g., `?side=pro`, `?side=yes`) → return **422**, not an empty list

### 404 handling

- Return 404 with `{"error": "Debate not found"}` when `debate_id` does not match any existing debate
- This applies to: `GET /debates/{debate_id}`, `POST /debates/{debate_id}/arguments`, `GET /debates/{debate_id}/arguments`

### Response envelopes

- List endpoints return a wrapper object, not a bare array:
  - `GET /debates` → `{"debates": [...], "total": N}`
  - `GET /debates/{id}/arguments` → `{"arguments": [...], "total": N}`
- `total` is the count of items in the returned list (after filtering)

### `argument_count` consistency

- `argument_count` on a Debate must equal the total number of Arguments in the database with that `debate_id`
- It is not filtered by side; it is always the full count

---

## Design Rationale

### 1. `"for"` / `"against"` over `"pro"` / `"con"` or a boolean

I chose `"for"` and `"against"` as the `side` values because they are unambiguous plain English that reads naturally in a debate context. `"pro"` and `"con"` are jargon that non-native English speakers find less intuitive. A boolean (e.g., `is_supporting: true/false`) would obscure intent and make filtering (`?side=for`) awkward to express. These two string literals are self-documenting at the API boundary.

### 2. `body` over `text`, `content`, or `argument` for the argument's text field

The field name `body` signals "the substantive text of this resource" — a convention established by HTTP (request/response body) and widely used in content-type APIs. `text` is ambiguous (plain text? formatted text?). `content` overloads with HTTP's Content-Type semantics. `argument` would create a naming collision with the resource type itself. `body` is the least ambiguous choice and is idiomatic in REST contracts.

### 3. `argument_count` as a denormalized field on Debate

Including `argument_count` directly on each Debate avoids forcing clients to issue N+1 queries (one per debate) to render a debate list with argument counts. The server maintains this as a running counter, incremented atomically when arguments are created. This is a deliberate trade-off: slight server-side complexity in exchange for a drastically simpler and more efficient client contract. The field is read-only and never accepted from clients to prevent count drift.

### 4. Envelope wrapper for list responses (`{"debates": [...], "total": N}`)

A bare JSON array is the simplest possible list response, but it forecloses future extensibility — you cannot add pagination cursors, metadata, or `total` counts without a breaking change. Wrapping with a named key and `total` now costs nothing and prevents a painful API version bump later. The key name matches the resource plural (`"debates"`, `"arguments"`), making the structure self-describing.

### 5. Opposing sort orders for debates vs. arguments

Debates are sorted newest-first because a debate list is a discovery interface — users want to see recent activity. Arguments within a debate are sorted oldest-first because within a debate, chronological order communicates the arc of the discussion: the sequence in which positions were staked matters. Reversing this would make the debate hard to follow. These are different information architectures requiring different orderings, not an inconsistency.
