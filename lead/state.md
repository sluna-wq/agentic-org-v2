# Lead State

Dynamic working memory. Updated by Lead each cycle.
Full decisions log: `lead/decisions.md` (newest first).

---

## Mandate

We are building an **Org Progress Dashboard** — a browser-based UI that lets the human see the real-time state of this agentic org: mandate, task board, decision log, and cycle history.

**Core requirements:**
- Single self-contained HTML file: `product/dashboard/index.html`
- No build step — open directly in browser or serve statically
- Reads live data from the GitHub API (no backend)
- Config: user enters `owner/repo` + optional GitHub PAT (saved to localStorage)
- Data sources: `lead/state.md`, `lead/decisions.md`, `lead/tasks/*/status.md`, `lead/tasks/*/package.md`, GitHub Actions runs

**What it shows:**
1. **Mandate panel** — current mandate parsed from `lead/state.md`
2. **Task board** — columns: Planned / Active / Review / Done with task cards (title, status, branch)
3. **Decisions feed** — parsed entries from `lead/decisions.md` (timestamp, action, what/why)
4. **Cycle timeline** — last 10 GitHub Actions workflow runs (name, status, duration, link)

**Quality bar:**
1. Works on a public repo with no PAT (unauthenticated GitHub API, 60 req/hr)
2. Works on a private repo when a PAT is supplied
3. Clean dark UI — readable at a glance, no clutter
4. Refresh button re-fetches all data without page reload
5. Graceful error states (rate limit message, repo not found, etc.)
6. `product/dashboard/README.md` with setup instructions

**Done means:** all 4 sections render correctly against this repo, config persists across page loads, errors surface clearly.

---

## Backlog

### Needs Human Input
<!-- Tasks or decisions blocked on human — describe exactly what's needed -->
*(none)*

### Planned
<!-- Priority order. Format: - [task-XXX] Description | P1/P2/P3 | deps: none -->
*(none)*

### Active
<!-- Format: - [task-XXX] Description | status | branch -->
*(none)*

### Done (recent)
<!-- Keep last ~10. Format: - [task-XXX] Description | accepted/discarded | YYYY-MM-DD -->
- [task-003] Org Progress Dashboard (single-file HTML, GitHub API) | accepted | 2026-03-01
- [task-002] Bookmark Manager REST API (Python/FastAPI) | accepted | 2026-03-01
- [task-001] Node.js REST API (items CRUD) | accepted | 2026-03-01

---

## Recent Decisions
<!-- Top 20 only — one line each. Full log in lead/decisions.md -->
<!-- Format: [YYYY-MM-DDTHH:MM] task-XXX ACTION — reason -->
- [2026-03-01T18:00] task-003 ACCEPTED — dashboard renders mandate, task board, decisions, cycle timeline; no PR (Think-mode session); accepted via direct diff
- [2026-02-28T12:00] MANDATE CHANGED — new mandate: Org Progress Dashboard (single-file HTML, GitHub API reads)
- [2026-02-28T12:00] task-003 ASSIGNED — build dashboard: mandate panel, task board, decisions feed, cycle timeline
- [2026-03-01T15:00] task-002 ACCEPTED — all 5 endpoints correct, AnyHttpUrl validation, tag filtering, pinned requirements.txt, README with curl examples; mandate complete
- [2026-03-01T14:00] LEAD CYCLE PASS — no review action; task-002 assigned, task agent not yet run
- [2026-03-01T13:00] task-002 ASSIGNED — implement Python/FastAPI bookmark manager (mandate not yet built)
- [2026-03-01T12:00] task-001 ACCEPTED — all 5 endpoints correct, clean 42-line implementation, no PR found so accepted via branch diff
- [2026-03-01T00:00] task-001 ASSIGNED — first task: bootstrap product context + implement full REST API (Express, in-memory)
