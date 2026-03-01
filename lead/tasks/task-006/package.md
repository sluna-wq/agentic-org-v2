# Task 006: Restructure repo to three-domain architecture

## System Prompt

You are a Build agent performing a structural infrastructure change to this agentic repo. This is NOT a product task — you are restructuring the repo's own orchestration layout. You will be modifying root-level files, log directories, CLAUDE.md, and orchestrator.sh.

**Expanded write access for this task only (explicitly authorized by Lead):**
- Root directory: `CLAUDE.md`, `orchestrator.sh`
- `logs/` directory (move/reorganize files)
- `lead/outbox.md` (new file to create)
- `lead/logs/build/` (new directory to create)
- Your own `lead/tasks/task-006/status.md`

## Assignment

Restructure the repository to a clean three-domain model with clear separation of channels and log directories by domain.

### Changes required

**1. Reorganize `logs/` into `logs/lead/`**
- Create `logs/lead/` directory
- Move all `logs/cycle-*.md` and `logs/cycle-*.jsonl` files → `logs/lead/` (currently: cycle-1.md, cycle-1.jsonl, cycle-2.md, cycle-2.jsonl)
- Leave `logs/.gitkeep` in place at `logs/`

**2. Update `orchestrator.sh` to write future Lead transcripts to `logs/lead/`**
- Find the line: `local transcript="$REPO_ROOT/logs/cycle-${CYCLE}.md"`
  (around line 222)
- Change it to: `local transcript="$REPO_ROOT/logs/lead/cycle-${CYCLE}.md"`
- Also add a `mkdir -p "$REPO_ROOT/logs/lead"` in the `preflight()` function so the directory always exists when the orchestrator starts.

**3. Create `lead/outbox.md`** — Lead's channel back to Think:
```markdown
# Lead → Think Outbox

<!-- Lead writes proposals, flags, and status updates here for Think to read. -->
<!-- Think reads and clears this file each session. -->

*(empty)*
```

**4. Create `lead/logs/build/` directory** — for future Build invocation logs:
- Add a `.gitkeep` file inside so the directory is tracked by git

**5. Update root `CLAUDE.md`** to reflect the three-domain write boundaries precisely:
- Think mode: writes to root `outbox.md` only
- Lead mode: writes to `lead/` only (including `lead/outbox.md`)
- Build mode: writes to `product/` and own `lead/tasks/<id>/status.md` only
- Make sure these boundaries are stated clearly in the mode descriptions

### Acceptance criteria
- [ ] `logs/lead/` exists and contains all cycle log files (cycle-1.md, cycle-1.jsonl, cycle-2.md, cycle-2.jsonl)
- [ ] No `logs/cycle-*.md` or `logs/cycle-*.jsonl` files remain at the root of `logs/`
- [ ] `orchestrator.sh` transcript path uses `logs/lead/cycle-${CYCLE}.md`
- [ ] `orchestrator.sh` `preflight()` creates `logs/lead/` with `mkdir -p`
- [ ] `lead/outbox.md` exists with the empty template (no queued content)
- [ ] `lead/logs/build/` exists with `.gitkeep`
- [ ] Root `CLAUDE.md` clearly states per-mode write boundaries (Think/Lead/Build)
- [ ] All changes committed to branch `task/006-repo-restructure`

## Relevant Files

- `CLAUDE.md` — update write boundary statements in each mode section
- `orchestrator.sh` — update transcript path (line ~222) and add mkdir -p in preflight
- `logs/` — move all cycle-*.md and cycle-*.jsonl files into `logs/lead/`
- `lead/outbox.md` — create new file
- `lead/logs/build/` — create new directory with .gitkeep
