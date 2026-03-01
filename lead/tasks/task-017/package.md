# Task 017: ADVERSARIAL Agent A — Debate Engine schema.md

## System Prompt

You are a Build agent working under the ADVERSARIAL topology in the Topology Research Program. You are Agent A — the schema author. You define the contract that Agents B and C will implement and then attack. Write a precise, explicit schema that leaves no room for ambiguity; an adversarial reviewer will try to find deviations in any implementation, so your schema must be the ground truth.

## Assignment

Write the API schema for the **Debate Engine** FastAPI API.

Write `product/debate-engine/adversarial/schema.md`.

### What to build

The Debate Engine allows users to create debate topics and post arguments for or against each topic. Define the complete REST API contract:

- `POST /api/v1/debates` — create a debate
- `GET /api/v1/debates` — list all debates
- `GET /api/v1/debates/{debate_id}` — get a single debate
- `POST /api/v1/debates/{debate_id}/arguments` — add an argument
- `GET /api/v1/debates/{debate_id}/arguments` — list arguments (with optional `?side=` filter)

### Acceptance criteria

- [ ] All 5 endpoints documented with: method, path, request body, response body (with example JSON), status codes
- [ ] Data models defined explicitly (Debate, Argument) with all field names, types, and constraints
- [ ] All status codes covered: 200, 201, 404, 422
- [ ] Error response shape defined: `{"error": "string"}`
- [ ] A "Notes for Agents B and C" section that explicitly enumerates constraints (field names, allowed values, server-generated fields, ordering rules, filter behavior) — this is the adversarial anchor that Agent C will use to find deviations
- [ ] Do NOT write api.py or any test files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/broadcast/schema.md` — reference for scope (do not copy; write fresh)
- `product/debate-engine/pipeline/schema.md` — reference for Notes section pattern (do not copy; write fresh)
