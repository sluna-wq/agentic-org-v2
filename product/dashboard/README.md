# Org Progress Dashboard

Live dashboard for this agentic org — mandate, task board, decisions log, and cycle timeline.

## Access

**GitHub Pages (primary):** https://sluna-wq.github.io/agentic-org-v2/

Auto-deployed after every orchestrator run. No setup needed — just visit the URL.

> First-time setup: go to **Settings → Pages → Source → GitHub Actions** in the repo to enable Pages.

**Locally:**
```
open product/dashboard/index.html
```

## Configuration

The dashboard defaults to `sluna-wq/agentic-org-v2` — loads automatically on first open.

| Field | Required | Notes |
|---|---|---|
| GitHub repo | Yes | Pre-filled. Change only if you fork. |
| Personal access token | No | For private repos or >60 req/hr rate limit. |

Config is saved to `localStorage`.

## What it shows

| Section | Source |
|---|---|
| **Mandate** | `lead/state.md` — current focus |
| **Task Board** | `lead/tasks/*/status.md` + `package.md` — Planned / Active / Review / Done |
| **Decisions** | `lead/decisions.md` — last 10 entries |
| **Cycle Timeline** | GitHub Actions runs — last 10, with status and duration |

## Getting a PAT (if needed)

Settings → Developer Settings → Fine-grained tokens → read access to: `Contents`, `Actions`, `Metadata`.
