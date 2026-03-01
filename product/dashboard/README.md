# Org Progress Dashboard

A single-file browser dashboard that shows the live state of this agentic org — mandate, task board, decisions log, and cycle timeline — by reading directly from the GitHub API.

## How to open it

**Locally:**
```
open product/dashboard/index.html
# or:
python3 -m http.server 8080 --directory product/dashboard
# then visit http://localhost:8080
```

**GitHub Pages:**
Enable Pages on the repo (Settings → Pages → Source: `main` branch, `/docs` folder or a deploy workflow), copy `index.html` to the configured location. No build step needed.

## Configuration

On first load you'll see a config bar at the top:

| Field | Required | Description |
|---|---|---|
| GitHub repo | Yes | `owner/repo` — e.g. `acme/agentic-org` |
| Personal access token | No* | Needed for private repos. Raises rate limit from 60 to 5000 req/hr. |

Config is saved to `localStorage` and auto-loaded on next visit.

## Getting a GitHub PAT

1. GitHub → Settings → Developer Settings → Personal access tokens → Fine-grained tokens
2. Create token with **read access** to: `Contents`, `Actions`, `Metadata`
3. Paste into the token field in the dashboard

## What it shows

| Section | Source |
|---|---|
| **Mandate** | `lead/state.md` (the `## Mandate` section) |
| **Task Board** | `lead/tasks/*/status.md` + `lead/tasks/*/package.md` — grouped into Planned / Active / Review / Done |
| **Decisions** | `lead/decisions.md` — last 10 entries |
| **Cycle Timeline** | GitHub Actions workflow runs — last 10, with status and duration |

## Dependencies

- [`marked.js`](https://marked.js.org/) via CDN (markdown rendering only) — loaded from `cdn.jsdelivr.net`
- GitHub REST API v3 (no API key needed for public repos)
