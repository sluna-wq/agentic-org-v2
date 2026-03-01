# Debate Engine API — Schema

**Pipeline role:** Agent A output. Agents B and C implement against this document.
**Base URL:** `/api/v1`
**Content-Type:** `application/json` for all request and response bodies.

---

## Data Models

### Debate

```json
{
  "id": "string (UUID)",
  "topic": "string",
  "description": "string",
  "created_at": "string (ISO 8601, e.g. 2026-03-01T12:00:00Z)"
}
```

### Argument

```json
{
  "id": "string (UUID)",
  "debate_id": "string (UUID)",
  "side": "\"for\" | \"against\"",
  "content": "string",
  "created_at": "string (ISO 8601, e.g. 2026-03-01T12:00:00Z)"
}
```

---

## Endpoints

---

### 1. Create a Debate

**POST** `/api/v1/debates`
Create a new debate topic.

**Request body:**
```json
{
  "topic": "string",
  "description": "string"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `topic` | string | yes | Short title for the debate |
| `description` | string | yes | Full description of the debate topic |

**Response `201 Created`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "AI should replace human judges",
  "description": "A debate about whether AI systems can and should replace human judges in legal proceedings.",
  "created_at": "2026-03-01T12:00:00Z"
}
```

---

### 2. List All Debates

**GET** `/api/v1/debates`
Return all debates, ordered by `created_at` descending.

**Request body:** none

**Response `200 OK`:**
```json
{
  "debates": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "topic": "AI should replace human judges",
      "description": "A debate about whether AI systems can and should replace human judges in legal proceedings.",
      "created_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `debates` | array | List of Debate objects; empty array `[]` when none exist |

---

### 3. Get a Single Debate

**GET** `/api/v1/debates/{debate_id}`
Return a single debate by its UUID.

**Path parameter:**

| Parameter | Type | Description |
|---|---|---|
| `debate_id` | string (UUID) | ID of the debate to retrieve |

**Request body:** none

**Response `200 OK`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "AI should replace human judges",
  "description": "A debate about whether AI systems can and should replace human judges in legal proceedings.",
  "created_at": "2026-03-01T12:00:00Z"
}
```

**Response `404 Not Found`:**
```json
{
  "error": "Debate not found"
}
```

---

### 4. Add an Argument to a Debate

**POST** `/api/v1/debates/{debate_id}/arguments`
Add a new argument (for or against) to an existing debate.

**Path parameter:**

| Parameter | Type | Description |
|---|---|---|
| `debate_id` | string (UUID) | ID of the debate to add the argument to |

**Request body:**
```json
{
  "side": "for",
  "content": "string"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `side` | `"for"` \| `"against"` | yes | Which side of the debate this argument supports |
| `content` | string | yes | The full text of the argument |

**Response `201 Created`:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "debate_id": "550e8400-e29b-41d4-a716-446655440000",
  "side": "for",
  "content": "AI has no emotional bias and can apply the law more consistently than human judges.",
  "created_at": "2026-03-01T12:05:00Z"
}
```

**Response `404 Not Found`:**
```json
{
  "error": "Debate not found"
}
```

---

### 5. List Arguments for a Debate

**GET** `/api/v1/debates/{debate_id}/arguments`
Return all arguments for a debate, ordered by `created_at` ascending.

**Path parameter:**

| Parameter | Type | Description |
|---|---|---|
| `debate_id` | string (UUID) | ID of the debate whose arguments to list |

**Query parameters (optional):**

| Parameter | Type | Description |
|---|---|---|
| `side` | `"for"` \| `"against"` | Filter arguments by side; omit to return both sides |

**Request body:** none

**Response `200 OK`:**
```json
{
  "arguments": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "debate_id": "550e8400-e29b-41d4-a716-446655440000",
      "side": "for",
      "content": "AI has no emotional bias and can apply the law more consistently than human judges.",
      "created_at": "2026-03-01T12:05:00Z"
    },
    {
      "id": "a87ff679-a2f3-71d4-e8b7-556655440001",
      "debate_id": "550e8400-e29b-41d4-a716-446655440000",
      "side": "against",
      "content": "Legal judgments require human empathy and contextual understanding that AI cannot replicate.",
      "created_at": "2026-03-01T12:07:00Z"
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `arguments` | array | List of Argument objects; empty array `[]` when none exist |

**Response `404 Not Found`:**
```json
{
  "error": "Debate not found"
}
```

---

## Status Code Summary

| Code | Meaning | Used on |
|---|---|---|
| `200` | OK | All read endpoints (GET) |
| `201` | Created | POST /debates, POST /debates/{id}/arguments |
| `404` | Not Found | Any endpoint referencing a `debate_id` that does not exist |
| `422` | Unprocessable Entity | Request body fails validation (missing required field, invalid `side` value) |

---

## Error Response Shape

All error responses use the same envelope:

```json
{
  "error": "string"
}
```

---

## Notes for Agents B and C

- All `id` fields are server-generated UUIDs. Clients never supply them.
- All `created_at` fields are server-generated ISO 8601 timestamps in UTC. Clients never supply them.
- The `side` field on Argument accepts exactly two values: `"for"` and `"against"`. Any other value should return `422`.
- The optional `?side=` query parameter on `GET /api/v1/debates/{debate_id}/arguments` narrows results by side. If omitted, both sides are returned together.
- Debate IDs and Argument IDs are independent UUID namespaces; do not conflate them.
