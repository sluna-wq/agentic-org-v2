# Task 009: Repo cleanup + orchestrator re-processing fix

## System Prompt

You are a Build agent performing cleanup and bug fixes on this agentic repo's infrastructure. You will archive stale task directories, fix a re-processing bug in orchestrator.sh, and remove an unused directory.

**Expanded write access for this task only (explicitly authorized by Lead):**
- `lead/tasks/` — archive task-001 through task-004 via git mv
- `orchestrator.sh` — fix process_lead_decisions() function
- `lead/logs/build/` — remove directory
- Your own `lead/tasks/task-009/status.md`

## Assignment

### Problem 1 — stale task directories

`lead/tasks/task-001` through `lead/tasks/task-004` are from obsolete mandates (Node.js REST API, Python bookmark manager, org dashboard, failed restructure). They add noise and confuse the Lead agent.

**Fix:** Archive them using `git mv`:
```bash
mkdir -p lead/tasks/archive
git mv lead/tasks/task-001 lead/tasks/archive/task-001
git mv lead/tasks/task-002 lead/tasks/archive/task-002
git mv lead/tasks/task-003 lead/tasks/archive/task-003
git mv lead/tasks/task-004 lead/tasks/archive/task-004
```

Keep `lead/tasks/task-005` and `lead/tasks/task-006` in place.

### Problem 2 — re-processing accepted/merged tasks

Every cycle, `process_lead_decisions()` in `orchestrator.sh` iterates over ALL tasks with `status=accepted` and tries to merge their PRs again (most already merged). This wastes API calls and causes noise.

**Fix in `orchestrator.sh`:**

1. In the merge loop inside `process_lead_decisions()`, before attempting to merge, check:
   ```bash
   local merged
   merged=$(get_field "$task_dir" "merged")
   if [[ "$merged" == "true" ]]; then
     log "  task $task_id already merged, skipping"
     continue
   fi
   ```

2. After a successful merge, set the field:
   ```bash
   set_field "$task_dir" "merged" "true"
   ```

Read the existing `process_lead_decisions()` function carefully before making changes — match the existing code style.

### Problem 3 — unused lead/logs/build/ directory

`lead/logs/build/` is an empty stub (`.gitkeep` only). Task transcripts already live at `lead/tasks/<id>/transcript.md`. Remove it:
```bash
git rm lead/logs/build/.gitkeep
```
Then commit without the directory (git will remove the empty dir automatically).

### Acceptance criteria
- [ ] `lead/tasks/archive/` contains task-001, task-002, task-003, task-004 (moved via git mv)
- [ ] `lead/tasks/task-005` and `lead/tasks/task-006` remain at `lead/tasks/`
- [ ] `orchestrator.sh` `process_lead_decisions()` checks `merged: true` before attempting PR merge
- [ ] After successful merge, `merged: true` is written to status.md via `set_field`
- [ ] `lead/logs/build/` directory removed

## Relevant Files

- `orchestrator.sh` — read `process_lead_decisions()` function carefully before editing
- `lead/tasks/task-001/` through `task-004/` — archive these
- `lead/tasks/task-005/`, `lead/tasks/task-006/` — leave these in place
- `lead/logs/build/.gitkeep` — remove this file
