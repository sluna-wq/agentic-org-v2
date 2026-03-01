# Task 003: Org Progress Dashboard

## System Prompt
You are a Build agent in an agentic software org. Your job is to implement the assigned feature cleanly and commit it. You write production-quality code, keep things simple, and do not over-engineer.

## Assignment

Build a single-file browser dashboard (`product/dashboard/index.html`) that lets the human see the real-time state of this agentic org by reading live data from the GitHub API.

### What to build

**File:** `product/dashboard/index.html` — fully self-contained (HTML + CSS + JS inline, no build step)

**Config panel (persisted to localStorage):**
- `owner/repo` input (e.g. `santiagoluna/agentic-org-v2`)
- Optional GitHub Personal Access Token (needed for private repos; raises rate limit to 5000/hr)
- A "Load / Refresh" button

**Four sections the dashboard must render:**

1. **Mandate panel** — parse and display the `## Mandate` section from `lead/state.md`
2. **Task board** — 4 columns: Planned / Active / Review / Done
   - Each task card shows: task ID, title (from package.md H1), status, branch
   - Source: `lead/tasks/*/status.md` + `lead/tasks/*/package.md`
3. **Decisions feed** — last 10 entries from `lead/decisions.md`
   - Each entry: timestamp, action label, what/why
4. **Cycle timeline** — last 10 GitHub Actions workflow runs
   - Each entry: run number, workflow name, status (with color), duration, link to run

### GitHub API approach

Use the Git Trees API to enumerate files in one call, then fetch only the blobs needed:

```
GET /repos/{owner}/{repo}/git/trees/main?recursive=1
```

Filter the tree for:
- `lead/state.md`
- `lead/decisions.md`
- all paths matching `lead/tasks/*/status.md`
- all paths matching `lead/tasks/*/package.md`

Fetch each blob by SHA:
```
GET /repos/{owner}/{repo}/git/blobs/{sha}
```
Content is base64-encoded — decode with `atob()`.

Actions runs:
```
GET /repos/{owner}/{repo}/actions/runs?per_page=10
```

Always set `Authorization: Bearer {token}` if a token is present.

### Parsing

- **state.md mandate**: extract text between `## Mandate` and the next `##` or `---` line
- **status.md**: simple `key: value` line parsing → `{status, branch, created, pr}`
- **package.md**: first H1 line is the task title; rest is description
- **decisions.md**: split on `## [` boundaries → parse timestamp + action from header line, body from content

### UI / UX

- Dark theme (background `#0d1117`, surface `#161b22`, accent `#238636`)
- Responsive single-column on narrow viewports, multi-column on wide
- Status badges with color: assigned=gray, in_progress=yellow, review=blue, accepted=green, discarded=red, changes_requested=orange
- Actions run status colors: success=green, failure=red, in_progress=yellow, cancelled=gray
- Show a loading spinner while fetching
- Show a clear error message for: rate limit hit (403/429), repo not found (404), network error
- `marked.min.js` via CDN for rendering markdown bodies (decisions, mandate)

### Acceptance criteria

1. Config (`owner/repo` + token) persists across page loads via localStorage
2. Mandate panel renders the mandate text from `lead/state.md`
3. Task board shows all tasks from `lead/tasks/` in the correct column
4. Decisions feed shows the last 10 entries from `lead/decisions.md`
5. Cycle timeline shows the last 10 Actions runs with status and link
6. Refresh button re-fetches without page reload
7. Works on a public repo with no token (unauthenticated)
8. Errors surface with a user-readable message (not a raw thrown exception)
9. `product/dashboard/README.md` exists with: what it is, how to open it, how to get a PAT

## Relevant Files

- `lead/state.md` — current mandate and backlog (your primary data source)
- `lead/decisions.md` — decisions log
- `lead/tasks/task-003/package.md` — this file
- `product/CLAUDE.md` — product context (update it to reflect the dashboard)
