# Debate Engine API — Schema

Base URL: `/`
All request and response bodies are JSON. All IDs are UUIDs (string).

---

## Data Types

### Debate

```json
{
  "id": "string (uuid)",
  "topic": "string",
  "description": "string",
  "created_at": "string (ISO 8601 datetime)"
}
```

### Argument

```json
{
  "id": "string (uuid)",
  "debate_id": "string (uuid)",
  "side": "\"for\" | \"against\"",
  "content": "string",
  "created_at": "string (ISO 8601 datetime)"
}
```

---

## Endpoints

### POST /debates

Create a new debate topic.

**Request body:**
```json
{
  "topic": "string",
  "description": "string"
}
```

**Response — 201 Created:**
```json
{
  "id": "string (uuid)",
  "topic": "string",
  "description": "string",
  "created_at": "string (ISO 8601 datetime)"
}
```

---

### GET /debates

List all debates.

**Request body:** none

**Response — 200 OK:**
```json
[
  {
    "id": "string (uuid)",
    "topic": "string",
    "description": "string",
    "created_at": "string (ISO 8601 datetime)"
  }
]
```

Returns an empty array `[]` if no debates exist.

---

### GET /debates/{debate_id}

Get a single debate by ID.

**Path parameter:** `debate_id` — UUID of the debate

**Request body:** none

**Response — 200 OK:**
```json
{
  "id": "string (uuid)",
  "topic": "string",
  "description": "string",
  "created_at": "string (ISO 8601 datetime)"
}
```

**Response — 404 Not Found:**
```json
{
  "detail": "Debate not found"
}
```

---

### POST /debates/{debate_id}/arguments

Add an argument to a debate.

**Path parameter:** `debate_id` — UUID of the debate

**Request body:**
```json
{
  "side": "\"for\" | \"against\"",
  "content": "string"
}
```

**Response — 201 Created:**
```json
{
  "id": "string (uuid)",
  "debate_id": "string (uuid)",
  "side": "\"for\" | \"against\"",
  "content": "string",
  "created_at": "string (ISO 8601 datetime)"
}
```

**Response — 404 Not Found:**
```json
{
  "detail": "Debate not found"
}
```

---

### GET /debates/{debate_id}/arguments

List all arguments for a debate.

**Path parameter:** `debate_id` — UUID of the debate

**Request body:** none

**Response — 200 OK:**
```json
[
  {
    "id": "string (uuid)",
    "debate_id": "string (uuid)",
    "side": "\"for\" | \"against\"",
    "content": "string",
    "created_at": "string (ISO 8601 datetime)"
  }
]
```

Returns an empty array `[]` if no arguments exist for this debate.

**Response — 404 Not Found:**
```json
{
  "detail": "Debate not found"
}
```
