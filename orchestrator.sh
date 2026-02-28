#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# CTO-Repo Orchestrator
# Stateless. All state lives in repo files.
# ─────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTO_DIR="$REPO_ROOT/cto"
TASKS_DIR="$CTO_DIR/tasks"
PRODUCT_DIR="$REPO_ROOT/product"
MAX_CYCLES="${MAX_CYCLES:-999}"
CYCLE=0

# ── Helpers ───────────────────────────────────

log() { echo "[orchestrator] $*"; }

# Commit all changes in the repo with a message
commit_all() {
  local msg="$1"
  cd "$REPO_ROOT"
  if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "$msg"
    log "Committed: $msg"
  else
    log "Nothing to commit for: $msg"
  fi
}

# Find all task folders with a given status
tasks_with_status() {
  local target_status="$1"
  for status_file in "$TASKS_DIR"/*/status.md; do
    [ -f "$status_file" ] || continue
    local status
    status=$(grep -m1 '^status:' "$status_file" | awk '{print $2}' | tr -d '[:space:]')
    if [ "$status" = "$target_status" ]; then
      dirname "$status_file"
    fi
  done
}

# Extract a field from status.md
get_status_field() {
  local status_file="$1/status.md"
  local field="$2"
  grep -m1 "^${field}:" "$status_file" | sed "s/^${field}:[[:space:]]*//" | tr -d '[:space:]'
}

# ── Phase 1: CTO ──────────────────────────────

run_cto_phase() {
  log "=== Phase 1: CTO (cycle $CYCLE) ==="

  local cto_prompt
  cto_prompt=$(cat <<'PROMPT'
[MODE:CTO]

You are the CTO. Read cto/CLAUDE.md fully before doing anything else.

Your tasks this cycle:
1. Review any tasks with status "review" — read their transcripts and code changes, then decide (accept / request changes / discard).
2. Update the backlog: prioritize, add new tasks if the mandate calls for it.
3. Assign the next highest-priority unblocked task(s) by writing their task packages under cto/tasks/.
4. Update cto/CLAUDE.md (backlog + recent decisions).
5. If the backlog is empty and there is no more work to do, write a file cto/NO_TASKS with a one-line reason.

Commit nothing — the orchestrator commits after you finish.
PROMPT
)

  # Invoke Claude Code in CTO mode
  # Transcript is printed to stdout; we capture it
  local transcript_file="$TASKS_DIR/../cto_cycle_${CYCLE}.transcript.md"
  claude --dangerously-skip-permissions \
    -p "$cto_prompt" \
    --output-format text \
    2>&1 | tee "$transcript_file"

  commit_all "cto: cycle $CYCLE — CTO pass"
}

# ── Phase 2: Tasks ────────────────────────────

run_task_phase() {
  log "=== Phase 2: Tasks (cycle $CYCLE) ==="

  local assigned_tasks
  assigned_tasks=$(tasks_with_status "assigned")

  if [ -z "$assigned_tasks" ]; then
    log "No assigned tasks to run."
    return 0
  fi

  while IFS= read -r task_dir; do
    [ -d "$task_dir" ] || continue
    local task_id
    task_id=$(basename "$task_dir")
    local package_file="$task_dir/package.md"
    local status_file="$task_dir/status.md"
    local transcript_file="$task_dir/transcript.md"

    log "--- Running $task_id ---"

    # Read the branch name from status.md
    local branch
    branch=$(get_status_field "$task_dir" "branch")

    # Create and checkout the task branch
    cd "$REPO_ROOT"
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
      git checkout "$branch"
    else
      git checkout -b "$branch"
    fi

    # Mark task as in_progress
    sed -i.bak 's/^status:.*/status: in_progress/' "$status_file" && rm -f "${status_file}.bak"
    commit_all "$task_id: mark in_progress"

    # Build the task prompt from the package
    local task_prompt
    task_prompt=$(cat <<PROMPT
[MODE:TASK]

Your task ID is: $task_id
Your git branch is: $branch

$(cat "$package_file")

---

When you are done:
- Make sure all your code is written to product/.
- Update cto/tasks/$task_id/status.md: change the status line to "status: review".
- Do not commit — the orchestrator handles git.
PROMPT
)

    # Run the task agent, capture full transcript
    claude --dangerously-skip-permissions \
      -p "$task_prompt" \
      --output-format text \
      2>&1 | tee "$transcript_file"

    # Ensure status was updated to review (task agent should do this, but verify)
    local current_status
    current_status=$(get_status_field "$task_dir" "status")
    if [ "$current_status" != "review" ]; then
      log "WARNING: $task_id did not set status to review. Setting it now."
      sed -i.bak 's/^status:.*/status: review/' "$status_file" && rm -f "${status_file}.bak"
    fi

    # Commit everything on the task branch
    commit_all "$task_id: task complete, status=review"

    # Return to main branch
    git checkout main

    log "--- $task_id done ---"

  done <<< "$assigned_tasks"
}

# ── Stop condition ────────────────────────────

should_stop() {
  # Stop if CTO wrote NO_TASKS
  if [ -f "$CTO_DIR/NO_TASKS" ]; then
    log "CTO wrote NO_TASKS: $(cat "$CTO_DIR/NO_TASKS")"
    return 0
  fi
  # Stop if cycle limit reached
  if [ "$CYCLE" -ge "$MAX_CYCLES" ]; then
    log "Max cycles ($MAX_CYCLES) reached."
    return 0
  fi
  return 1
}

# ── Main loop ─────────────────────────────────

main() {
  log "Starting orchestrator. Repo: $REPO_ROOT"

  # Ensure we're on main and repo is initialized
  cd "$REPO_ROOT"
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log "Initializing git repo..."
    git init
    git add -A
    git commit -m "chore: initial repo structure"
  fi

  # Ensure main branch exists
  if ! git show-ref --verify --quiet refs/heads/main; then
    git checkout -b main 2>/dev/null || git checkout main
  fi

  while true; do
    CYCLE=$((CYCLE + 1))
    log "====== Cycle $CYCLE ======"

    run_cto_phase

    if should_stop; then
      log "Stopping."
      break
    fi

    run_task_phase

    if should_stop; then
      log "Stopping."
      break
    fi

    log "Cycle $CYCLE complete. Looping..."
  done

  log "Orchestrator finished after $CYCLE cycle(s)."
}

main "$@"
