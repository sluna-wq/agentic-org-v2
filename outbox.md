# Think → Lead Outbox

<!-- Think writes directions here for Lead to read and act on. -->
<!-- Lead clears this file after reading. -->

## New Mandate — 2026-03-01

**Goal:** Four deliverables that make this org production-quality. Assign as three parallel-safe tasks (different files, no conflicts).

---

### task-007: Fix orchestrator + deploy dashboard to GitHub Pages

**Problem 1 — env var bug:** `.github/workflows/orchestrator.yml` passes `CTO_MAX_TURNS` and `TASK_MAX_TURNS` as env vars, but `orchestrator.sh` reads `LEAD_MAX_TURNS` and `BUILD_MAX_TURNS`. Fix both names to match: rename workflow inputs and env vars to `lead_max_turns` / `build_max_turns` (matching orchestrator.sh exactly).

**Problem 2 — no native dashboard access:** Deploy `product/dashboard/index.html` to GitHub Pages so it's accessible at `https://sluna-wq.github.io/agentic-org-v2/`.

Implementation:
1. Fix env var names in `.github/workflows/orchestrator.yml` (CTO_MAX_TURNS→LEAD_MAX_TURNS, TASK_MAX_TURNS→BUILD_MAX_TURNS in both `inputs:` section and `env:` block).
2. Add a second job `deploy-pages` to the workflow (runs after `run` job succeeds):
   - Needs permissions: `pages: write` and `id-token: write` (add to top-level permissions block)
   - Steps: `actions/checkout@v4` → copy `product/dashboard/index.html` to a staging dir → `actions/upload-pages-artifact@v3` → `actions/deploy-pages@v4`
3. In `product/dashboard/index.html`, set the default config values: `owner = 'sluna-wq'`, `repo = 'agentic-org-v2'` so the dashboard works immediately when loaded from Pages without any configuration. Find the localStorage config load / default section in the JS and set these defaults.
4. In `product/dashboard/README.md`, add the Pages URL prominently at top: `https://sluna-wq.github.io/agentic-org-v2/`

Acceptance criteria:
- `orchestrator.yml` env vars match `orchestrator.sh` variable names exactly
- `deploy-pages` job exists in the workflow with correct permissions and steps
- Dashboard HTML has owner=sluna-wq and repo=agentic-org-v2 as defaults
- README.md has the Pages URL

Files to edit: `.github/workflows/orchestrator.yml`, `product/dashboard/index.html`, `product/dashboard/README.md`

---

### task-008: Architecture diagram

Create `ARCHITECTURE.md` at repo root. One page, crisp ASCII art. Show the full system: how Think → Lead → Build → PR → merge flows, what each domain owns, and how the orchestrator drives it all.

Required sections:
1. **Flow diagram** — ASCII showing the cycle: Think (human + Claude) writes outbox.md → orchestrator.sh invokes Lead (Claude) → Lead writes task packages → orchestrator invokes Build (Claude) → Build commits to branch → orchestrator opens PR → Lead reviews → orchestrator merges → main updated
2. **Domain map** — what lives in each of the three domains: `lead/` (state, tasks, decisions), `product/` (all built artifacts), `logs/` (transcripts)
3. **One-sentence description** of each agent role (Think, Lead, Build, Orchestrator)

Style: no fluff, no prose paragraphs beyond one-liners. Max 80 chars wide. Elegant.

Acceptance criteria:
- File exists at `ARCHITECTURE.md`
- Has a readable ASCII flow diagram that shows the full cycle
- Has the three-domain map
- Under 120 lines total

Files to create: `ARCHITECTURE.md`

---

### task-009: Repo cleanup + orchestrator re-processing fix

**Problem 1 — stale task directories:** `lead/tasks/task-001` through `lead/tasks/task-004` are from obsolete mandates (Node.js REST API, Python bookmark manager, failed restructure). They add noise and confuse the Lead agent. Archive them: move to `lead/tasks/archive/` (git mv).

Keep: task-005 and task-006 (recent, legitimate). Archive: task-001, task-002, task-003, task-004.

**Problem 2 — re-processing accepted/merged tasks:** Every cycle, `process_lead_decisions()` in `orchestrator.sh` iterates over ALL tasks with status=accepted and tries to merge their PRs again (most already merged). Fix: after a successful merge, set a field `merged: true` in status.md so the orchestrator skips it in subsequent cycles. In the merge loop, check `get_field "$task_dir" "merged"` and skip if it equals "true". After successful merge, call `set_field "$task_dir" "merged" "true"`.

**Problem 3 — lead/logs/build/ is unused:** The `lead/logs/build/` directory exists as a stub (.gitkeep only) with no content. Either start using it (build transcripts should go there, not in `lead/tasks/`) OR remove it to keep things honest. Decision: remove it (it's empty, it's not being used by the orchestrator, and task transcripts already live at `lead/tasks/<id>/transcript.md`). Delete `lead/logs/build/.gitkeep` and the directory.

Acceptance criteria:
- `lead/tasks/archive/` contains task-001 through task-004 (moved via git mv)
- task-005 and task-006 remain at `lead/tasks/`
- `orchestrator.sh` `process_lead_decisions()` checks `merged: true` before attempting PR merge
- After successful merge, `merged: true` is set in status.md
- `lead/logs/build/` directory removed

Files to edit: `orchestrator.sh`, various `lead/tasks/` dirs

---

## Priority order

Assign all three tasks this cycle. They touch different files — no conflicts.
Lead should assign task-007, task-008, and task-009 simultaneously.
Clear this outbox after reading.
