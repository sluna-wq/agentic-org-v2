# Decisions Log

Newest first. Each entry: timestamp, task, action, what was decided and why (concise).

---

## [2026-03-01T23:55] task-006 ACCEPTED — three-domain repo restructure complete
**What:** Reviewed PR #3 (branch task/006-repo-restructure) via branch diff. All 8 acceptance criteria met: (1) logs/lead/ created with all four cycle logs moved via git rename; (2) no cycle-*.md/jsonl remain at logs/ root; (3) orchestrator.sh transcript path → logs/lead/cycle-${CYCLE}.md; (4) preflight() now mkdir -p logs/lead; (5) lead/outbox.md created with empty template; (6) lead/logs/build/.gitkeep created; (7) CLAUDE.md write boundaries clarified for all three modes; (8) all committed to task/006-repo-restructure. gh self-review blocked (single-author GitHub env, established precedent); accepted via branch diff.
**Why:** Clean, minimal implementation. Every structural change required by the three-domain architecture spec was delivered correctly. Backlog now empty; NO_TASKS written.

---

## [2026-03-01T23:50] task-006 ASSIGNED — repo restructure (re-run from main)
**What:** Read outbox.md direction from Think: PR #1 (task-004) was already closed (confirmed CLOSED via gh); structural changes never landed on main. Confirmed: `logs/lead/` missing, `lead/outbox.md` missing, cycle logs still at `logs/` root. Created task-006 with same spec as task-004, updated to include cycle-2 files and correct branch `task/006-repo-restructure`. Cleared outbox.md. Removed NO_TASKS stop signal. Deleted `lead/NO_TASKS` and `lead/NO_TASKS.md`.
**Why:** Think explicitly directed re-assignment after PR #1 conflict. Fresh branch from current main (which has task-005 merge gate fix) avoids the original conflict.

---

## [2026-03-01T23:45] LEAD CYCLE PASS — backlog empty, awaiting mandate
**What:** Full cycle run. No tasks in `review` status (all are `accepted`). No tasks in `planned` or `active`. `lead/NO_TASKS` already in place. Updated "Needs Human Input" in state.md to explicitly flag that next mandate is required.
**Why:** Nothing to do until human sets direction. Org is idle and healthy.

---

## [2026-03-01T23:30] task-005 ACCEPTED — orchestrator merge gate fixed
**What:** Reviewed PR #2 (branch task/005-fix-merge-gate) via `git diff main...task/005-fix-merge-gate`. All 6 acceptance criteria verified: `reviewDecision` variable and `gh pr view --json reviewDecision` call removed; accepted PRs now merge immediately on `status.md=accepted`; "no PR number recorded — skipping merge" guard retained; comment updated to "trust status.md: accepted as merge authority"; `outbox.md` cleared to empty template; no other logic changed. `gh pr review --approve` blocked by GitHub self-review restriction (single-author environment, same as task-004). Accepted via branch diff per established precedent.
**Why:** Clean surgical 5-line edit. Merge gate is now correct — Lead's status.md decision is sole authority. Backlog now empty; writing NO_TASKS.

---

## [2026-03-01T23:00] task-005 ASSIGNED — fix orchestrator merge gate
**What:** Read direction from root `outbox.md` (commit 5ec5cdb, authored by human in Think mode): remove the `reviewDecision` check from `process_lead_decisions()` in `orchestrator.sh`. Currently the orchestrator only merges accepted PRs when GitHub's `reviewDecision=APPROVED`, but GitHub blocks self-review in single-author environments, so no PR ever auto-merges. Fix: merge on `status.md: accepted` alone; drop the `gh pr view --json reviewDecision` gate entirely. Build agent also clears `outbox.md` back to empty template. Created task-005 on branch `task/005-fix-merge-gate`. Deleted `lead/NO_TASKS` stop signal.
**Why:** The merge gate is broken by design in this single-author GitHub environment. Every accepted task stays blocked. The fix is a 5-line surgical edit to orchestrator.sh — low risk, high value. Lead's status.md decision is the authority; GitHub review is redundant here.

---

## [2026-03-01T22:00] task-004 ACCEPTED — three-domain repo restructure
**What:** Reviewed PR #1 (branch task/004-repo-restructure) via `git diff main...task/004-repo-restructure`. All 9 acceptance criteria verified: `logs/lead/` contains cycle-1 files; old `logs/cycle-1.*` removed; `orchestrator.sh` transcript path updated to `logs/lead/cycle-${CYCLE}.md` and `preflight()` has `mkdir -p logs/lead`; `lead/outbox.md` created with correct template; `lead/logs/build/.gitkeep` present; root `CLAUDE.md` explicitly states per-mode read/write boundaries for Think/Lead/Build; root `outbox.md` cleared to empty template. `gh pr review --approve` blocked by GitHub's self-review restriction (same single-author environment as prior tasks). Accepted via branch diff per established precedent (task-002, task-003).
**Why:** Implementation is correct and complete. Three-domain architecture is now in place. Backlog is empty — writing NO_TASKS. Human input needed to set next mandate.

---

## [2026-03-01T21:00] task-004 ASSIGNED — repo restructure to three-domain architecture
**What:** Read `outbox.md` queued by Think. Direction: restructure repo to three-domain model with `logs/lead/` for Lead logs, `lead/outbox.md` for Lead→Think channel, `lead/logs/build/` for Build logs, updated `CLAUDE.md` write boundaries, and cleared `outbox.md`. Created task-004 with expanded write scope (root CLAUDE.md, outbox.md, orchestrator.sh, logs/, lead/ structural files). Deleted `lead/NO_TASKS` stop signal. Updated mandate in state.md.
**Why:** Think explicitly queued this direction via outbox.md. It's a pure housekeeping task — no product changes. The three-domain separation makes write boundaries unambiguous and gives each mode a clear communication channel. Spec is tight; Build has a concrete checklist and can complete this in one pass.

---

## [2026-03-01T20:00] LEAD CYCLE PASS — mandate complete, backlog empty
**What:** Reviewed all task statuses. task-001, task-002, task-003 all accepted. No tasks in review, active, or planned. Mandate (Org Progress Dashboard) fully delivered. Writing NO_TASKS stop signal.
**Why:** Backlog is done. Nothing to assign. Human input needed to set next mandate before work can continue.

---

## [2026-03-01T18:00] task-003 ACCEPTED
**What:** Reviewed `product/dashboard/index.html` (single-file, ~550 lines HTML+CSS+JS). Implements all 4 required sections: mandate panel (parsed from lead/state.md), task board with Planned/Active/Review/Done columns (from lead/tasks/*/status.md + package.md via Git Trees API), decisions feed (last 10 from lead/decisions.md), cycle timeline (GitHub Actions runs). Config persists to localStorage. Works unauthenticated on public repos. Error states for rate limit, 404, network failures. Refresh button re-fetches. `product/dashboard/README.md` present with setup and PAT instructions.
**Why:** All 6 acceptance criteria met. No PR was created — task ran in Think-mode session rather than via orchestrator; accepted via branch diff. This is a known deviation for this initial bootstrap cycle; future tasks should run through orchestrator.

---

## [2026-02-28T12:00] MANDATE CHANGED + task-003 ASSIGNED
**What:** Prior mandate (bookmark manager REST API) is complete. New mandate is the Org Progress Dashboard — a single-file browser app (`product/dashboard/index.html`) that reads live org state from the GitHub API and renders: mandate panel, task board (Planned/Active/Review/Done columns), decisions feed, and cycle timeline (GitHub Actions runs). No build step. Works unauthenticated on public repos; PAT stored in localStorage for private repos or higher rate limits. task-003 created and assigned to branch `task/003-dashboard`.
**Why:** Human wants to see the org's progress on the product in real time. The source of truth is already in this repo (lead/state.md, lead/decisions.md, lead/tasks/, GitHub Actions). An in-house static dashboard reading the GitHub API is the right fit — no external service needed, no sync drift, zero infra, deployable to GitHub Pages.

---

## [2026-03-01T15:00] task-002 ACCEPTED
**What:** Reviewed `product/main.py` (64 lines), `product/requirements.txt`, `product/README.md`, and `product/CLAUDE.md` via `git diff main...task/002-bookmark-api`. All 5 endpoints implemented correctly (GET /health, POST /bookmarks, GET /bookmarks with ?tag filter, GET /bookmarks/{id}, DELETE /bookmarks/{id}). `AnyHttpUrl` validation rejects bad URLs with 422. Tag filtering uses `if tag in b["tags"]` — correct exact match. Requirements pinned (fastapi==0.115.14, uvicorn==0.34.3, pydantic==2.12.5). README has curl examples for all 5 endpoints. CLAUDE.md updated with layout and run instructions. POST returns 201. Both 404 paths correct.
**Why:** All 5 acceptance criteria met. No PR was created by the task agent (gh pr list returned empty) so accepted via branch diff. Mandate is now fully complete — no remaining planned tasks.

---

## [2026-03-01T14:00] LEAD CYCLE PASS — no review action
**What:** Lead cycle ran. task-002 is in `assigned` state — no branch, no PR exists yet. Task agent has not executed. No tasks in `review`. Backlog: Planned empty, Active has task-002 only.
**Why:** Nothing to review or assign. Waiting on orchestrator to invoke the task agent for task-002.

---

## [2026-03-01T13:00] task-002 ASSIGNED
**What:** Created task-002 to implement the bookmark manager REST API in Python using FastAPI with in-memory storage. Covers all 5 endpoints (GET /health, POST /bookmarks, GET /bookmarks with tag filter, GET /bookmarks/{id}, DELETE /bookmarks/{id}), Pydantic AnyHttpUrl validation, pinned requirements.txt, README.md with curl examples, and product/CLAUDE.md update.
**Why:** Mandate is set and product/ only has a stub CLAUDE.md — no implementation exists. Backlog was empty. This is the primary deliverable.

---

## [2026-03-01T12:00] task-001 ACCEPTED
**What:** Reviewed `product/index.js`, `product/package.json`, and `product/CLAUDE.md` via `git diff main...task/001-rest-api`. All 5 endpoints implemented correctly (GET /health, GET /items, POST /items, GET /items/:id, DELETE /items/:id). Validation: POST returns 400 for missing/empty/non-string name. 404s correct on GET and DELETE. Server starts on port 3000. Code is 42 lines — clean, readable, no bloat. CLAUDE.md fully filled in.
**Why:** All acceptance criteria met. No PR was created by the task agent (gh pr list returned empty) so accepted via branch diff. No changes requested.

---

## [2026-03-01T00:00] task-001 ASSIGNED
**What:** Created task-001 to bootstrap `product/CLAUDE.md` and implement the full REST API (Express, in-memory storage). Single combined task: fill in product context then deliver all 5 endpoints (GET /health, GET /items, POST /items, GET /items/:id, DELETE /items/:id) with proper error handling (400 for bad input, 404 for missing items).
**Why:** Backlog was empty, no tasks existed. Mandate is clear and self-contained. Combining bootstrap + implementation into one task avoids unnecessary round-trips on a simple greenfield project.

---

*(empty — Lead prepends entries here each cycle)*
