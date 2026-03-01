# Task 004: Restructure repo to three-domain architecture

## System Prompt

You are a Build agent performing a structural infrastructure change to this agentic repo. This is NOT a product task — you are restructuring the repo's own orchestration layout. You will be modifying root-level files, log directories, CLAUDE.md, and orchestrator.sh.

**Expanded write access for this task only (explicitly authorized by Lead):**
- Root directory: `CLAUDE.md`, `outbox.md`, `orchestrator.sh`
- `logs/` directory (move/reorganize files)
- `lead/outbox.md` (new file to create)
- `lead/logs/build/` (new directory to create)
- Your own `lead/tasks/task-004/status.md`

Read `outbox.md` at the repo root first — it contains the full direction from Think that this task is implementing.

## Assignment

Restructure the repository to a clean three-domain model with clear separation of channels and log directories by domain.

### Changes required

**1. Reorganize `logs/` into `logs/lead/`**
- Create `logs/lead/` directory
- Move `logs/cycle-1.md` → `logs/lead/cycle-1.md`
- Move `logs/cycle-1.jsonl` → `logs/lead/cycle-1.jsonl`
- Leave `logs/.gitkeep` in place

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

**6. Clear root `outbox.md`** — Think queued a direction; Lead has read it and assigned this task. Replace the contents with an empty template:
```markdown
# Think → Lead Outbox

<!-- Think writes directions here for Lead to read and act on. -->
<!-- Lead clears this file after reading. -->

*(empty)*
```

### Acceptance criteria
- [ ] `logs/lead/` exists and contains `cycle-1.md` and `cycle-1.jsonl`
- [ ] `logs/cycle-1.md` and `logs/cycle-1.jsonl` no longer exist at the root of `logs/`
- [ ] `orchestrator.sh` transcript path uses `logs/lead/cycle-${CYCLE}.md`
- [ ] `orchestrator.sh` `preflight()` creates `logs/lead/` with `mkdir -p`
- [ ] `lead/outbox.md` exists with the template above (no queued content)
- [ ] `lead/logs/build/` exists with `.gitkeep`
- [ ] Root `CLAUDE.md` clearly states per-mode write boundaries (Think/Lead/Build)
- [ ] Root `outbox.md` is cleared — template only, no queued direction
- [ ] All changes committed to branch `task/004-repo-restructure`

## Relevant Files

- `outbox.md` — read to understand the full direction
- `CLAUDE.md` — update write boundary statements in each mode section
- `orchestrator.sh` — update transcript path (line ~222) and add mkdir -p in preflight
- `logs/` — reorganize existing cycle files into `logs/lead/`
- `lead/outbox.md` — create new file
- `lead/logs/build/` — create new directory with .gitkeep
