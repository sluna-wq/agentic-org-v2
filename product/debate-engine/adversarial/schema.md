# Debate Engine API — Schema v1.0

**Base URL:** `/api/v1`
**Content-Type:** All request and response bodies are `application/json`.

---

## Data Models

### Debate

| Field        | Type     | Constraints                                      |
|--------------|----------|--------------------------------------------------|
| `id`         | string   | Server-generated UUID v4; immutable              |
| `title`      | string   | Required; 1–200 characters; leading/trailing whitespace stripped |
| `description`| string   | Required; 1–2000 characters; leading/trailing whitespace stripped |
| `created_at` | string   | Server-generated ISO 8601 UTC datetime (`YYYY-MM-DDTHH:MM:SS.ffffffZ`); immutable |

**Example:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Pineapple belongs on pizza",
  "description": "A debate on the merits of pineapple as a pizza topping.",
  "created_at": "2026-03-01T12:00:00.000000Z"
}
```

---

### Argument

| Field        | Type     | Constraints                                                                 |
|--------------|----------|-----------------------------------------------------------------------------|
| `id`         | string   | Server-generated UUID v4; immutable                                         |
| `debate_id`  | string   | UUID v4; must reference an existing debate; immutable                       |
| `side`       | string   | Exactly one of: `"for"` or `"against"`; case-sensitive; immutable           |
| `body`       | string   | Required; 1–1000 characters; leading/trailing whitespace stripped           |
| `created_at` | string   | Server-generated ISO 8601 UTC datetime (`YYYY-MM-DDTHH:MM:SS.ffffffZ`); immutable |

**Example:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "debate_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "side": "for",
  "body": "Pineapple adds a sweet contrast that complements the salty cheese.",
  "created_at": "2026-03-01T12:05:00.000000Z"
}
```

---

### Error Response

All error responses use this shape:

```json
{
  "error": "string"
}
```

The `error` field is a human-readable message. No additional fields are present.

---

## Endpoints

---

### POST /api/v1/debates

Create a new debate.

**Request Body:**

| Field         | Type   | Required | Constraints                      |
|---------------|--------|----------|----------------------------------|
| `title`       | string | Yes      | 1–200 characters                 |
| `description` | string | Yes      | 1–2000 characters                |

**Example request:**
```json
{
  "title": "Pineapple belongs on pizza",
  "description": "A debate on the merits of pineapple as a pizza topping."
}
```

**Response — 201 Created:**

Returns the newly created Debate object.

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Pineapple belongs on pizza",
  "description": "A debate on the merits of pineapple as a pizza topping.",
  "created_at": "2026-03-01T12:00:00.000000Z"
}
```

**Response — 422 Unprocessable Entity:**

Returned when the request body fails validation (missing fields, wrong types, constraint violations).

```json
{
  "error": "title is required"
}
```

---

### GET /api/v1/debates

List all debates.

**Request Body:** None.
**Query Parameters:** None.

**Response — 200 OK:**

Returns a JSON array of Debate objects, ordered by `created_at` ascending (oldest first). Returns an empty array `[]` when no debates exist.

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "Pineapple belongs on pizza",
    "description": "A debate on the merits of pineapple as a pizza topping.",
    "created_at": "2026-03-01T12:00:00.000000Z"
  },
  {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "title": "Tabs vs spaces",
    "description": "Which indentation style is superior?",
    "created_at": "2026-03-01T13:00:00.000000Z"
  }
]
```

---

### GET /api/v1/debates/{debate_id}

Get a single debate by ID.

**Path Parameters:**

| Parameter   | Type   | Description                 |
|-------------|--------|-----------------------------|
| `debate_id` | string | UUID v4 of the debate       |

**Request Body:** None.

**Response — 200 OK:**

Returns the Debate object.

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Pineapple belongs on pizza",
  "description": "A debate on the merits of pineapple as a pizza topping.",
  "created_at": "2026-03-01T12:00:00.000000Z"
}
```

**Response — 404 Not Found:**

Returned when no debate with the given `debate_id` exists.

```json
{
  "error": "Debate not found"
}
```

---

### POST /api/v1/debates/{debate_id}/arguments

Add an argument to a debate.

**Path Parameters:**

| Parameter   | Type   | Description                 |
|-------------|--------|-----------------------------|
| `debate_id` | string | UUID v4 of the debate       |

**Request Body:**

| Field  | Type   | Required | Constraints                                     |
|--------|--------|----------|-------------------------------------------------|
| `side` | string | Yes      | Exactly `"for"` or `"against"`; case-sensitive  |
| `body` | string | Yes      | 1–1000 characters                               |

**Example request:**
```json
{
  "side": "for",
  "body": "Pineapple adds a sweet contrast that complements the salty cheese."
}
```

**Response — 201 Created:**

Returns the newly created Argument object. The `debate_id` field in the response must equal the `debate_id` from the path.

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "debate_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "side": "for",
  "body": "Pineapple adds a sweet contrast that complements the salty cheese.",
  "created_at": "2026-03-01T12:05:00.000000Z"
}
```

**Response — 404 Not Found:**

Returned when no debate with the given `debate_id` exists.

```json
{
  "error": "Debate not found"
}
```

**Response — 422 Unprocessable Entity:**

Returned when the request body fails validation (missing fields, wrong types, invalid `side` value, constraint violations).

```json
{
  "error": "side must be 'for' or 'against'"
}
```

---

### GET /api/v1/debates/{debate_id}/arguments

List arguments for a debate, with an optional side filter.

**Path Parameters:**

| Parameter   | Type   | Description                 |
|-------------|--------|-----------------------------|
| `debate_id` | string | UUID v4 of the debate       |

**Query Parameters:**

| Parameter | Type   | Required | Constraints                                              |
|-----------|--------|----------|----------------------------------------------------------|
| `side`    | string | No       | If present, must be exactly `"for"` or `"against"`; filters results to that side only |

**Request Body:** None.

**Response — 200 OK:**

Returns a JSON array of Argument objects, ordered by `created_at` ascending (oldest first). Returns an empty array `[]` when no matching arguments exist (including when `?side=` filter matches nothing). The `debate_id` field of every returned argument must equal the path `debate_id`.

Without filter:
```json
[
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "debate_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "side": "for",
    "body": "Pineapple adds a sweet contrast that complements the salty cheese.",
    "created_at": "2026-03-01T12:05:00.000000Z"
  },
  {
    "id": "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed",
    "debate_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "side": "against",
    "body": "Fruit has no place on a savoury dish.",
    "created_at": "2026-03-01T12:06:00.000000Z"
  }
]
```

With `?side=for`:
```json
[
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "debate_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "side": "for",
    "body": "Pineapple adds a sweet contrast that complements the salty cheese.",
    "created_at": "2026-03-01T12:05:00.000000Z"
  }
]
```

**Response — 404 Not Found:**

Returned when no debate with the given `debate_id` exists. This applies regardless of whether `?side=` is supplied.

```json
{
  "error": "Debate not found"
}
```

**Response — 422 Unprocessable Entity:**

Returned when `?side=` is present but its value is not `"for"` or `"against"`.

```json
{
  "error": "side must be 'for' or 'against'"
}
```

---

## Status Code Summary

| Code | Meaning              | When used                                                                      |
|------|----------------------|--------------------------------------------------------------------------------|
| 200  | OK                   | Successful GET                                                                 |
| 201  | Created              | Successful POST (debate or argument created)                                   |
| 404  | Not Found            | `debate_id` does not exist in any endpoint that accepts it as a path parameter |
| 422  | Unprocessable Entity | Request body or query parameter fails validation                               |

---

## Notes for Agents B and C

This section is the authoritative adversarial anchor. Any implementation deviation from the rules below is a defect.

### Field names and types

1. Debate fields: `id`, `title`, `description`, `created_at` — exactly these four, no extras, no renames.
2. Argument fields: `id`, `debate_id`, `side`, `body`, `created_at` — exactly these five, no extras, no renames.
3. `id` and `debate_id` are strings (UUID v4 format). Do not return integers or any other type.
4. `created_at` is a string in ISO 8601 UTC format ending in `Z`. Do not return Unix timestamps or other date formats.

### Server-generated fields

5. `id` is always assigned by the server. Clients must not supply it; if supplied it must be silently ignored, not reflected back.
6. `created_at` is always assigned by the server at creation time. Clients must not supply it; if supplied it must be silently ignored, not reflected back.
7. `debate_id` on an Argument is set from the path parameter `debate_id`, never from the request body.

### Allowed values for `side`

8. The only valid values for `side` are the string `"for"` and the string `"against"`. Both are lowercase; no other capitalisation is accepted.
9. `"For"`, `"FOR"`, `"Against"`, `"AGAINST"`, `"pro"`, `"con"`, and all other variants are invalid and must return 422.

### Ordering

10. `GET /api/v1/debates` must return debates ordered by `created_at` ascending (oldest first).
11. `GET /api/v1/debates/{debate_id}/arguments` (with or without `?side=`) must return arguments ordered by `created_at` ascending (oldest first).
12. No other sort orders are supported; clients cannot control ordering.

### Filter behaviour

13. `?side=` is the only supported query parameter on the arguments list endpoint.
14. When `?side=for` is supplied, only arguments with `side == "for"` are returned.
15. When `?side=against` is supplied, only arguments with `side == "against"` are returned.
16. When `?side=` is absent, all arguments for the debate are returned.
17. An invalid `?side=` value (anything other than `"for"` or `"against"`) returns 422, even if the debate does not exist. 404 takes precedence over 422 only for the path parameter `debate_id`; the `?side=` query parameter is validated independently.
18. Other unrecognised query parameters must be silently ignored (they do not cause a 422).

### 404 vs 422 precedence

19. If `debate_id` does not exist and the request body is also invalid, the response is 404, not 422.
20. Existence of the debate must be checked before validating the argument request body.

### Error response shape

21. All non-2xx responses must use exactly `{"error": "string"}`. No additional top-level fields (e.g. `detail`, `message`, `errors`) are permitted.
22. The value of `error` is a non-empty string. An empty string is not acceptable.

### Input sanitisation

23. Leading and trailing whitespace in `title`, `description`, and `body` must be stripped before storage and before length validation. A value of `"  "` (spaces only) fails the minimum-length constraint after stripping and must return 422.
24. Length constraints are enforced on the stripped value: `title` 1–200 chars, `description` 1–2000 chars, `body` 1–1000 chars.

### Response codes for POST success

25. Both `POST /api/v1/debates` and `POST /api/v1/debates/{debate_id}/arguments` must return **201**, not 200.

### No partial responses

26. Every endpoint returns the complete object (all fields listed above). Partial objects (e.g. omitting `created_at`) are non-compliant.
