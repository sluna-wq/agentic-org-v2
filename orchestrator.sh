#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# CTO-Repo Orchestrator — stateless, autonomous
# All state lives in the repo. No human input
# needed during a run.
# ─────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTO_DIR="$REPO_ROOT/cto"
TASKS_DIR="$CTO_DIR/tasks"
MAX_CYCLES="${MAX_CYCLES:-999}"
CTO_MAX_TURNS="${CTO_MAX_TURNS:-40}"
TASK_MAX_TURNS="${TASK_MAX_TURNS:-60}"
CYCLE=0

# ── Pre-flight ────────────────────────────────

preflight() {
  # Require claude CLI
  if ! command -v claude &>/dev/null; then
    echo "[orchestrator] ERROR: 'claude' CLI not found. Install it and ensure it's on PATH."
    exit 1
  fi

  # Ensure git user is set (needed for unattended commits)
  if [ -z "$(git config user.email 2>/dev/null || true)" ]; then
    git config user.email "orchestrator@cto-repo.local"
    git config user.name "CTO Orchestrator"
  fi

  # Init repo if needed
  cd "$REPO_ROOT"
  if ! git rev-parse --git-dir &>/dev/null; then
    git init
    git add -A
    git commit -m "chore: initial repo structure"
  fi

  # Ensure we're on main
  if ! git show-ref --verify --quiet refs/heads/main; then
    git checkout -b main 2>/dev/null || true
  fi
  git checkout main
}

# ── Helpers ───────────────────────────────────

log() { echo "[orchestrator] $*"; }

commit_all() {
  local msg="$1"
  cd "$REPO_ROOT"
  if ! git diff --quiet HEAD 2>/dev/null || \
     [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "$msg"
    log "Committed: $msg"
  else
    log "Nothing to commit for: $msg"
  fi
}

# Return task dirs matching a status (space-separated list)
tasks_with_status() {
  local target="$1"
  for f in "$TASKS_DIR"/*/status.md; do
    [ -f "$f" ] || continue
    local s
    s=$(grep -m1 '^status:' "$f" | awk '{print $2}' | tr -d '[:space:]')
    [ "$s" = "$target" ] && dirname "$f"
  done
}

get_field() {
  local dir="$1" field="$2"
  grep -m1 "^${field}:" "$dir/status.md" \
    | sed "s/^${field}:[[:space:]]*//" \
    | tr -d '[:space:]'
}

# ── Phase 1: CTO ──────────────────────────────

run_cto_phase() {
  log "=== Phase 1: CTO (cycle $CYCLE) ==="

  local cto_prompt
  cto_prompt=$(cat <<'PROMPT'
[MODE:CTO]

Read cto/CLAUDE.md fully before doing anything else. That is your context.

This cycle:
1. Review all tasks with status "review":
   - Read their package.md and diff the branch vs main in product/.
   - Decide: accept, request changes, or discard.
   - Log each decision to cto/decisions.md (prepend — newest first) with timestamp, what was decided, and why.
   - Add a one-liner to "Recent Decisions" in cto/CLAUDE.md (keep only top 20 there).
2. Update the backlog sections in cto/CLAUDE.md (Planned / Active / Done / Needs Human Input).
3. Assign the next highest-priority unblocked Planned task(s):
   - Write cto/tasks/task-XXX/package.md and cto/tasks/task-XXX/status.md (status: assigned).
   - Move that task to the Active section of the backlog.
4. If the backlog is empty and all work is done, write cto/NO_TASKS with one line explaining why.

Rules:
- Do not commit — orchestrator handles git.
- Do not write to product/.
- If anything requires human input, add it to the "Needs Human Input" backlog section.
PROMPT
)

  local transcript="$CTO_DIR/cto_cycle_${CYCLE}.transcript.md"
  claude --dangerously-skip-permissions \
    --max-turns "$CTO_MAX_TURNS" \
    -p "$cto_prompt" \
    --output-format text \
    2>&1 | tee "$transcript"

  commit_all "cto: cycle $CYCLE — CTO pass"
}

# ── Phase 2: Tasks ────────────────────────────

run_task_phase() {
  log "=== Phase 2: Tasks (cycle $CYCLE) ==="

  # Collect assigned tasks AND changes_requested tasks (both need to run)
  local runnable=()
  while IFS= read -r d; do runnable+=("$d"); done < <(tasks_with_status "assigned")
  while IFS= read -r d; do runnable+=("$d"); done < <(tasks_with_status "changes_requested")

  if [ ${#runnable[@]} -eq 0 ]; then
    log "No runnable tasks."
    return 0
  fi

  for task_dir in "${runnable[@]}"; do
    [ -d "$task_dir" ] || continue
    local task_id branch package_file status_file transcript_file
    task_id=$(basename "$task_dir")
    branch=$(get_field "$task_dir" "branch")
    package_file="$task_dir/package.md"
    status_file="$task_dir/status.md"
    transcript_file="$task_dir/transcript.md"

    log "--- Running $task_id (branch: $branch) ---"

    cd "$REPO_ROOT"
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
      git checkout "$branch"
    else
      git checkout -b "$branch"
    fi

    # Mark in_progress
    sed -i.bak "s/^status:.*/status: in_progress/" "$status_file" && rm -f "${status_file}.bak"
    commit_all "$task_id: mark in_progress"

    # Build prompt — if changes_requested, append prior transcript
    local extra=""
    if [ -f "$transcript_file" ]; then
      extra=$(printf '\n\n## Prior Transcript\n\n%s' "$(cat "$transcript_file")")
    fi

    local task_prompt
    task_prompt=$(cat <<PROMPT
[MODE:TASK]

Task ID: $task_id
Branch: $branch

$(cat "$package_file")${extra}

---

When done:
- All code changes must be in product/.
- Set cto/tasks/$task_id/status.md status line to: status: review
- Do not commit — orchestrator handles git.
PROMPT
)

    # Run task agent, capture transcript
    claude --dangerously-skip-permissions \
      --max-turns "$TASK_MAX_TURNS" \
      -p "$task_prompt" \
      --output-format text \
      2>&1 | tee "$transcript_file"

    # Safety: ensure status was set to review
    local current
    current=$(get_field "$task_dir" "status")
    if [ "$current" != "review" ]; then
      log "WARNING: $task_id did not set status=review. Forcing it."
      sed -i.bak "s/^status:.*/status: review/" "$status_file" && rm -f "${status_file}.bak"
    fi

    commit_all "$task_id: complete, status=review"
    git checkout main
    log "--- $task_id done ---"
  done
}

# ── Stop condition ────────────────────────────

should_stop() {
  if [ -f "$CTO_DIR/NO_TASKS" ]; then
    log "CTO signaled done: $(cat "$CTO_DIR/NO_TASKS")"
    return 0
  fi
  if [ "$CYCLE" -ge "$MAX_CYCLES" ]; then
    log "Max cycles ($MAX_CYCLES) reached."
    return 0
  fi
  return 1
}

# ── Main ──────────────────────────────────────

main() {
  log "Starting. Repo: $REPO_ROOT"
  log "claude max-turns: CTO=$CTO_MAX_TURNS  Task=$TASK_MAX_TURNS"
  preflight

  while true; do
    CYCLE=$((CYCLE + 1))
    log "====== Cycle $CYCLE ======"

    run_cto_phase
    should_stop && { log "Stopping after CTO phase."; break; }

    run_task_phase
    should_stop && { log "Stopping after task phase."; break; }

    log "Cycle $CYCLE complete."
  done

  log "Orchestrator finished after $CYCLE cycle(s)."
}

main "$@"
