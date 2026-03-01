# Task 020: SPECIALIST Agent A — Debate Engine schema.md

## System Prompt

You are a Build agent working under the SPECIALIST topology in the Topology Research Program. You are Agent A — a Senior REST API Designer. Your specialization is contract design: versioning, resource modelling, constraint specification, and error handling. You apply REST principles deliberately, not just by convention. You think carefully about what makes a schema unambiguous and implementable. Write the schema that you, as a specialist, believe is the highest-quality contract for this API.

## Assignment

Write the API schema for the **Debate Engine** FastAPI API.

Write `product/debate-engine/specialist/schema.md`.

### What to build

The Debate Engine allows users to create debate topics and post arguments for or against each topic. Define the complete REST API contract:

- `POST /api/v1/debates` — create a debate
- `GET /api/v1/debates` — list all debates
- `GET /api/v1/debates/{debate_id}` — get a single debate
- `POST /api/v1/debates/{debate_id}/arguments` — add an argument
- `GET /api/v1/debates/{debate_id}/arguments` — list arguments (with optional `?side=` filter)

Apply your expertise as a REST API designer. Make deliberate choices about field names, constraints, and error handling. Document the reasoning behind any non-obvious design decisions.

### Acceptance criteria

- [ ] All 5 endpoints documented with: method, path, request body, response body (with example JSON), status codes
- [ ] Data models defined explicitly (Debate, Argument) with all field names, types, and constraints
- [ ] All status codes covered: 200, 201, 404, 422
- [ ] Error response shape defined: `{"error": "string"}`
- [ ] A "Notes for Agent B" section that enumerates constraints Agent B must implement exactly (field names, allowed values, server-generated fields, ordering rules, filter behavior) — written from your specialist perspective on what matters most
- [ ] A "Design Rationale" section explaining at least 3 deliberate design decisions you made (e.g., field naming choices, constraint choices, ordering decisions)
- [ ] Do NOT write api.py or any test files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/broadcast/schema.md` — reference for scope (do not copy; write fresh as a specialist)
- `product/debate-engine/pipeline/schema.md` — reference (do not copy; apply your own specialist judgment)
- `product/debate-engine/adversarial/schema.md` — reference (do not copy; apply your own specialist judgment)
