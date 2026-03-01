# Task 012: BROADCAST Agent B — Debate Engine ui.html

## System Prompt

You are a Build agent working under the BROADCAST topology in the Topology Research Program. Your team has three agents — you are Agent B (UI). Agents A and C are working in parallel and independently on the same Debate Engine: do not coordinate with them. This isolation is the controlled experimental condition.

**CRITICAL:** Do NOT read any files that may exist under `product/debate-engine/broadcast/`. Those are other agents' outputs. You must independently invent your understanding of the Debate Engine API. Your choice of routes, field names, and status codes is the research data point.

## Assignment

Build a **Debate Engine UI** as a single-file HTML + JS app.

Write `product/debate-engine/broadcast/ui.html`.

### What to build

The Debate Engine concept: a backend service where users can create debate topics, post arguments for or against each topic, and retrieve debates and arguments. Your UI consumes a REST API at a configurable base URL (default: `http://localhost:8000`).

Required UI capabilities:
- List all debates
- View a single debate and its arguments (for vs. against)
- Create a new debate (topic + description)
- Post an argument on a debate (side: for or against, content)

### Acceptance criteria

- [ ] Single self-contained file — inline CSS + JS, no npm, no bundler, no CDN scripts
- [ ] API base URL is configurable (hardcoded default `http://localhost:8000` or an input field)
- [ ] All four capabilities (list, view, create debate, post argument) are implemented
- [ ] At the top of the `<script>` section, a comment block documents the exact API routes your UI calls (method, path, request/response shape) — this is the research measurement artifact
- [ ] Errors from fetch calls are displayed to the user (not silently swallowed)
- [ ] Do NOT write api.py or tests — those are other agents' responsibilities

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- No existing files in `product/debate-engine/broadcast/` — do not read them even if they appear
