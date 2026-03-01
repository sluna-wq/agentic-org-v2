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

### Problem 4 — orchestrator NO_TASKS robustness

After `run_lead_phase()`, if Lead forgets to delete `lead/NO_TASKS` while having assigned tasks, the orchestrator stops early (as just happened with task-007/008/009).

**Fix in `orchestrator.sh`:** In the main loop, between the `run_lead_phase` call and `should_stop()`, add a safeguard that deletes `lead/NO_TASKS` if any tasks have status `assigned` or `changes_requested`:

```bash
# Safety: if Lead assigned tasks but forgot to remove NO_TASKS, clear it
if [ -n "$(tasks_with_status "assigned"; tasks_with_status "changes_requested")" ]; then
  rm -f "$LEAD_DIR/NO_TASKS" "$LEAD_DIR/NO_TASKS.md"
  log "Safety: removed stale NO_TASKS (runnable tasks exist)"
fi
```

Read the main loop in `orchestrator.sh` carefully to find the correct insertion point.

Also add `orchestrator.sh` to the **Expanded write access** list above.

### Acceptance criteria
- [ ] `lead/tasks/archive/` contains task-001, task-002, task-003, task-004 (moved via git mv)
- [ ] `lead/tasks/task-005` and `lead/tasks/task-006` remain at `lead/tasks/`
- [ ] `orchestrator.sh` `process_lead_decisions()` checks `merged: true` before attempting PR merge
- [ ] After successful merge, `merged: true` is written to status.md via `set_field`
- [ ] `lead/logs/build/` directory removed
- [ ] `orchestrator.sh` main loop: stale NO_TASKS removed when runnable tasks (`assigned` or `changes_requested`) exist

## Relevant Files

- `orchestrator.sh` — read `process_lead_decisions()` and the main loop before editing
- `lead/tasks/task-001/` through `task-004/` — archive these
- `lead/tasks/task-005/`, `lead/tasks/task-006/` — leave these in place
- `lead/logs/build/.gitkeep` — remove this file
