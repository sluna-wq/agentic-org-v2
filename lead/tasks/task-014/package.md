# Task 014: PIPELINE Agent A — Debate Engine schema.md

## System Prompt

You are a Build agent working under the PIPELINE topology in the Topology Research Program. You are Agent A — the first link in the pipeline. Agents B and C will receive your output and build on it sequentially. Write a clear, precise API contract: they depend on it directly.

## Assignment

Design the **Debate Engine** API contract.

Write `product/debate-engine/pipeline/schema.md`.

### What to build

The Debate Engine concept: a backend service where users can create debate topics, post arguments for or against each topic, and retrieve debates and arguments.

Minimum endpoints required (you may add more if they fit naturally):
- Create a debate (topic + description)
- List all debates
- Get a single debate by ID
- Add an argument to a debate (side: "for" | "against", content)
- List arguments for a debate

`schema.md` must describe every endpoint: method, path, request body JSON shape, response JSON shape, status codes, and a one-line description. This document is the source of truth for the entire pipeline — Agents B and C will read it and implement against it.

### Acceptance criteria

- [ ] `schema.md` documents every endpoint with method, path, request/response JSON, and status codes
- [ ] Field names are explicit (do not leave them ambiguous)
- [ ] Status codes specified: 201 for creates, 200 for reads, 404 for not-found
- [ ] Do NOT write api.py, ui.html, or tests — this task is schema only

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/broadcast/schema.md` — the BROADCAST version for reference (you may read it, but write your own clean version for the pipeline)
- No existing files in `product/debate-engine/pipeline/` — you are creating it from scratch
