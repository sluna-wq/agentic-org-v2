# Think → Lead Outbox

<!-- Think writes directions here for Lead to read and act on. -->
<!-- Lead clears this file after reading. -->

## Addendum to task-009 — 2026-03-01

Add the following fix to task-009's package.md scope before the Build agent runs it:

**Problem 4 — orchestrator NO_TASKS robustness:** After `run_lead_phase()`, if Lead forgets to delete `lead/NO_TASKS` while having assigned tasks, the orchestrator stops early. Fix in `orchestrator.sh`: after `run_lead_phase()` and before `should_stop()`, add a safeguard that deletes `lead/NO_TASKS` if any tasks have status `assigned` or `changes_requested`.

Add to `orchestrator.sh` in the main loop between `run_lead_phase` and `process_lead_decisions`:
```bash
# Safety: if Lead assigned tasks but forgot to remove NO_TASKS, clear it
if [ -n "$(tasks_with_status "assigned"; tasks_with_status "changes_requested")" ]; then
  rm -f "$LEAD_DIR/NO_TASKS" "$LEAD_DIR/NO_TASKS.md"
  log "Safety: removed stale NO_TASKS (runnable tasks exist)"
fi
```

This just caused a real stop: Lead assigned task-007/008/009 but left NO_TASKS in place — Build never ran.

Otherwise tasks proceed as specified. Read, update task-009's package.md, clear this outbox, proceed.
