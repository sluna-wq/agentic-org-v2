#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# CTO-Repo Orchestrator
#
# Commit strategy (explicit):
#   Task agents   → commit code to their branch as they work
#   Orchestrator  → pushes branch, opens PR when task completes
#   Orchestrator  → squash-merges PR when CTO accepts
#   Orchestrator  → closes + deletes branch when CTO discards
#   Orchestrator  → commits cto/ changes directly to main
#
# Main branch only ever receives accepted, squash-merged PRs.
# ─────────────────────────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTO_DIR="$REPO_ROOT/cto"
TASKS_DIR="$CTO_DIR/tasks"
MAX_CYCLES="${MAX_CYCLES:-999}"
CTO_MAX_TURNS="${CTO_MAX_TURNS:-40}"
TASK_MAX_TURNS="${TASK_MAX_TURNS:-60}"
CYCLE=0

# ── Pre-flight ────────────────────────────────────────────────────

preflight() {
  local missing=()
  command -v claude  &>/dev/null || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
  command -v gh      &>/dev/null || missing+=("gh (https://cli.github.com)")
  command -v git     &>/dev/null || missing+=("git")
  command -v python3 &>/dev/null || missing+=("python3")

  if [ ${#missing[@]} -gt 0 ]; then
    echo "[orchestrator] ERROR: missing required tools:"
    for t in "${missing[@]}"; do echo "  - $t"; done
    exit 1
  fi

  if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "[orchestrator] ERROR: ANTHROPIC_API_KEY is not set."
    exit 1
  fi

  # Set git identity if not configured (needed for unattended runs)
  [ -n "$(git config user.email 2>/dev/null || true)" ] || \
    git config user.email "orchestrator@cto-repo.local"
  [ -n "$(git config user.name  2>/dev/null || true)" ] || \
    git config user.name "CTO Orchestrator"

  # Init git repo if needed
  cd "$REPO_ROOT"
  if ! git rev-parse --git-dir &>/dev/null; then
    git init
    git add -A
    git commit -m "chore: initial repo structure"
  fi

  # Ensure we start on main
  if ! git show-ref --verify --quiet refs/heads/main; then
    git checkout -b main 2>/dev/null || true
  fi
  git checkout main

  log "Pre-flight OK. Claude max-turns: CTO=$CTO_MAX_TURNS Task=$TASK_MAX_TURNS"
}

# ── Helpers ───────────────────────────────────────────────────────

log() { echo "[orchestrator] $*"; }

# Convert claude's stream-json output to readable markdown.
# Reads from stdin, writes to stdout.
# Usage: claude ... --output-format stream-json | jsonl_to_md "label" | tee transcript.md
jsonl_to_md() {
  python3 "$REPO_ROOT/scripts/jsonl_to_md.py" "$1"
}

# Run a claude session, capturing full stream-json + formatted markdown transcript.
#
# $1 label        — human-readable name for the transcript header
# $2 prompt       — the full prompt string
# $3 max_turns    — --max-turns value
# $4 out_md       — path to write formatted markdown transcript (also shown in terminal)
#
# Raw stream-json is written to ${out_md%.md}.jsonl alongside the markdown.
# Both files are committed to the repo for full auditability.
run_claude() {
  local label="$1" prompt="$2" max_turns="$3" out_md="$4"
  local out_jsonl="${out_md%.md}.jsonl"

  # Pipeline:
  #   claude -> tee(raw jsonl) -> jsonl_to_md -> tee(transcript md + terminal)
  claude --dangerously-skip-permissions \
    --max-turns "$max_turns" \
    -p "$prompt" \
    --output-format stream-json \
    --verbose \
    2>&1 \
    | tee "$out_jsonl" \
    | jsonl_to_md "$label" \
    | tee "$out_md"
}

# Extract the "Final Output" section from a prior transcript jsonl.
# Used for revision context — we inject the summary, not the full tool log.
extract_final_output() {
  local jsonl="$1"
  [ -f "$jsonl" ] || return 0
  python3 -c "
import sys, json
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    try:
        e = json.loads(line)
        if e.get('type') == 'result':
            print(e.get('result', ''))
    except: pass
" "$jsonl" 2>/dev/null || true
}

# Commit anything pending in the repo to current branch
commit_all() {
  local msg="$1"
  cd "$REPO_ROOT"
  # Stage everything including deletions
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "$msg"
    log "Committed: $msg"
  else
    log "Nothing to commit: $msg"
  fi
}

# Push current branch to origin
push_branch() {
  local branch="$1"
  git push -u origin "$branch" 2>&1 || {
    log "WARNING: push failed for $branch — continuing anyway (may be local-only run)"
  }
}

# Return task dirs matching a given status, one per line
tasks_with_status() {
  local target="$1"
  for f in "$TASKS_DIR"/*/status.md; do
    [ -f "$f" ] || continue
    local s
    s=$(grep -m1 '^status:' "$f" | awk '{print $2}' | tr -d '[:space:]')
    [ "$s" = "$target" ] && dirname "$f"
  done
}

# Read a field from a task's status.md
get_field() {
  local task_dir="$1" field="$2"
  grep -m1 "^${field}:" "$task_dir/status.md" \
    | sed "s/^${field}:[[:space:]]*//" \
    | tr -d '[:space:]' \
    || echo ""
}

# Write or update a field in status.md
set_field() {
  local task_dir="$1" field="$2" value="$3"
  local file="$task_dir/status.md"
  if grep -q "^${field}:" "$file" 2>/dev/null; then
    sed -i.bak "s|^${field}:.*|${field}: ${value}|" "$file" && rm -f "${file}.bak"
  else
    echo "${field}: ${value}" >> "$file"
  fi
}

# ── Phase 1a: CTO reviews and assigns ─────────────────────────────

run_cto_phase() {
  log "=== Phase 1: Lead (cycle $CYCLE) ==="
  cd "$REPO_ROOT"
  git checkout main

  local cto_prompt
  cto_prompt=$(cat <<'PROMPT'
[MODE:LEAD]

Read cto/CLAUDE.md and cto/state.md fully before doing anything else.

This cycle — do all that apply:

1. REVIEW tasks in "review" status:
   - Read status.md (get PR number + branch). Read package.md (recall assignment).
   - Review code: `gh pr diff PR_NUMBER` or `git diff main...BRANCH -- product/`
   - Submit your decision as a GitHub PR review — this is the merge gate:
     * Accept  → `gh pr review PR_NUMBER --approve --body "reason"`; set status: accepted in status.md
     * Changes → `gh pr review PR_NUMBER --request-changes --body "numbered list of what must change"`; set status: changes_requested in status.md
     * Discard → set status: discarded in status.md with reason (orchestrator closes the PR)
   - Your GitHub review body is what the next agent sees. Write feedback clearly and specifically.
   - Log every decision to cto/decisions.md (prepend, newest first):
     Format: ## [TIMESTAMP] task-XXX ACTION\n**What:** ...\n**Why:** ...
   - Add one-liner to "Recent Decisions" in cto/state.md (keep top 20 only).

2. UPDATE the backlog in cto/state.md:
   - Move accepted/discarded tasks to Done section.
   - Move changes_requested tasks back to Active.
   - Flag anything blocked on human input in "Needs Human Input" section.

3. ASSIGN next tasks from Planned:
   - Pick highest-priority unblocked tasks.
   - Create cto/tasks/task-XXX/ with package.md and status.md (status: assigned).
   - Move them to Active section in backlog.

4. STOP signal: if backlog is fully done and nothing to assign, write cto/NO_TASKS.

Rules:
- Do not commit — orchestrator handles all git operations.
- Do not write to product/.
- Be concise. cto/state.md is your working memory, keep it clean.
PROMPT
)

  local transcript="$REPO_ROOT/logs/cycle-${CYCLE}.md"
  run_claude "lead-cycle-${CYCLE}" "$cto_prompt" "$CTO_MAX_TURNS" "$transcript"

  # Commit all Lead changes (decisions, backlog, new task packages) to main
  commit_all "lead: cycle $CYCLE — review + assign"
  push_branch main
}

# ── Phase 1b: Merge or close PRs based on CTO decisions ──────────

process_cto_decisions() {
  log "=== Phase 1b: Processing CTO decisions ==="
  cd "$REPO_ROOT"
  git checkout main

  # Merge accepted PRs — only if CTO has approved them on GitHub
  while IFS= read -r task_dir; do
    [ -d "$task_dir" ] || continue
    local task_id branch pr_number review_decision
    task_id=$(basename "$task_dir")
    branch=$(get_field "$task_dir" "branch")
    pr_number=$(get_field "$task_dir" "pr")

    if [ -z "$pr_number" ]; then
      log "$task_id: accepted but no PR number recorded — skipping merge"
      continue
    fi

    # Verify the CTO actually approved on GitHub (this is the real gate)
    review_decision=$(gh pr view "$pr_number" \
      --json reviewDecision --jq '.reviewDecision' 2>/dev/null || echo "")

    if [ "$review_decision" = "APPROVED" ]; then
      log "$task_id: PR #$pr_number is GitHub-approved — squash merging"
      gh pr merge "$pr_number" --squash --delete-branch \
        --subject "$task_id: $(head -1 "$task_dir/package.md" | sed 's/^# //')" \
        2>&1 || log "WARNING: could not merge PR #$pr_number (may already be merged)"
    else
      log "BLOCKED: $task_id PR #$pr_number status.md=accepted but GitHub reviewDecision=$review_decision"
      log "  → CTO must run: gh pr review $pr_number --approve"
    fi
  done < <(tasks_with_status "accepted")

  # Close discarded PRs
  while IFS= read -r task_dir; do
    [ -d "$task_dir" ] || continue
    local task_id branch pr_number
    task_id=$(basename "$task_dir")
    branch=$(get_field "$task_dir" "branch")
    pr_number=$(get_field "$task_dir" "pr")

    if [ -n "$pr_number" ] && [ "$pr_number" != "" ]; then
      log "$task_id: closing PR #$pr_number (discarded)"
      gh pr close "$pr_number" --comment "Discarded by CTO. See cto/tasks/$task_id/status.md." \
        --delete-branch 2>&1 || log "WARNING: could not close PR #$pr_number"
    fi
  done < <(tasks_with_status "discarded")

  # Pull main after merges
  git pull --rebase origin main 2>/dev/null || true
}

# ── Phase 2: Run task agents ──────────────────────────────────────

run_task_phase() {
  log "=== Phase 2: Tasks (cycle $CYCLE) ==="

  # Run both newly assigned tasks AND tasks needing changes
  local runnable=()
  while IFS= read -r d; do [ -d "$d" ] && runnable+=("$d"); done < <(tasks_with_status "assigned")
  while IFS= read -r d; do [ -d "$d" ] && runnable+=("$d"); done < <(tasks_with_status "changes_requested")

  if [ ${#runnable[@]} -eq 0 ]; then
    log "No runnable tasks this cycle."
    return 0
  fi

  for task_dir in "${runnable[@]}"; do
    local task_id branch package_file status_file transcript_file pr_number
    task_id=$(basename "$task_dir")
    branch=$(get_field "$task_dir" "branch")
    package_file="$task_dir/package.md"
    status_file="$task_dir/status.md"
    transcript_file="$task_dir/transcript.md"

    log "--- Running $task_id (branch: $branch) ---"
    cd "$REPO_ROOT"

    # Switch to or create the task branch
    git checkout main
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
      git checkout "$branch"
    else
      git checkout -b "$branch"
    fi

    # Mark in_progress and commit to main bookkeeping
    set_field "$task_dir" "status" "in_progress"
    # We need to commit status change — but we're on the task branch.
    # Keep cto/ status updates on the task branch too; orchestrator will
    # commit them after merging or on cleanup.
    git add -A
    git diff --cached --quiet || git commit -m "$task_id: mark in_progress"

    # Build the task prompt
    # For revisions: pull CTO's feedback from the GitHub PR review (that's the source of truth)
    local revision_context=""
    local current_task_status
    current_task_status=$(get_field "$task_dir" "status")
    pr_number=$(get_field "$task_dir" "pr")

    if [ "$current_task_status" = "changes_requested" ] && [ -n "$pr_number" ]; then
      local cto_feedback
      cto_feedback=$(gh pr view "$pr_number" --json reviews \
        --jq '[.reviews[] | select(.state=="CHANGES_REQUESTED")] | last | .body' \
        2>/dev/null || echo "")
      if [ -n "$cto_feedback" ]; then
        revision_context=$(printf '\n\n---\n\n## CTO Review Feedback (from GitHub PR #%s)\n\n%s' \
          "$pr_number" "$cto_feedback")
      fi
    fi

    # For revisions: inject only the final output summary from the prior session,
    # not the full tool log — keeps tokens manageable.
    local prior_jsonl="${transcript_file%.md}.jsonl"
    local prior_summary
    prior_summary=$(extract_final_output "$prior_jsonl")
    if [ -n "$prior_summary" ]; then
      revision_context="${revision_context}"$(printf '\n\n---\n\n## Prior Session Summary\n\n%s' "$prior_summary")
    elif [ -f "$transcript_file" ]; then
      # Fallback: no jsonl yet (first run before this change), use full md transcript
      revision_context="${revision_context}"$(printf '\n\n---\n\n## Prior Transcript\n\n%s' "$(cat "$transcript_file")")
    fi

    local task_prompt
    task_prompt=$(cat <<PROMPT
[MODE:TASK]

Task ID  : $task_id
Branch   : $branch

$(cat "$package_file")${revision_context}

---

Instructions:
- Read product/CLAUDE.md before writing any code.
- Write all code changes to product/.
- Commit your work to this branch as you go (git add + git commit with clear messages).
  Do NOT push — the orchestrator handles push and PR creation.
- When done, set the status field in cto/tasks/$task_id/status.md to: review
  (just update that one field — the orchestrator will commit it with the rest)
PROMPT
)

    # Run the task agent — it commits its own code changes
    run_claude "$task_id" "$task_prompt" "$TASK_MAX_TURNS" "$transcript_file"

    # Safety: force status=review if agent forgot
    local current_status
    current_status=$(get_field "$task_dir" "status")
    if [ "$current_status" != "review" ]; then
      log "WARNING: $task_id did not set status=review. Forcing."
      set_field "$task_dir" "status" "review"
    fi

    # Commit transcript + status update on the task branch
    git add -A
    git diff --cached --quiet || git commit -m "$task_id: transcript + status=review"

    # Push the task branch to origin
    push_branch "$branch"

    # Open or update the PR
    pr_number=$(get_field "$task_dir" "pr")
    if [ -z "$pr_number" ]; then
      # New PR — use --body-file to avoid shell escaping issues with markdown content
      local pr_title pr_url
      pr_title=$(head -1 "$package_file" | sed 's/^# //')
      pr_url=$(gh pr create \
        --title "$pr_title" \
        --body-file "$package_file" \
        --base main \
        --head "$branch" 2>&1) && {
        # gh pr create prints the PR URL on success — extract number from it
        pr_number=$(echo "$pr_url" | grep -oE '[0-9]+$' || echo "")
      } || {
        log "WARNING: gh pr create failed for $task_id — $pr_url"
        pr_url=""
      }

      if [ -n "$pr_number" ]; then
        set_field "$task_dir" "pr" "$pr_number"
        git add -A
        git diff --cached --quiet || git commit -m "$task_id: record PR #$pr_number"
        push_branch "$branch"
        log "$task_id: opened PR #$pr_number"
      else
        log "WARNING: no PR number for $task_id — CTO will review via branch diff"
      fi
    else
      # Revision — PR already open, push is enough
      log "$task_id: pushed revision to existing PR #$pr_number"
    fi

    # Return to main
    git checkout main

    # Sync the status.md update back to main so the CTO sees it next cycle
    git checkout "$branch" -- "cto/tasks/$task_id/status.md" 2>/dev/null || true
    git add -A
    git diff --cached --quiet || git commit -m "$task_id: sync status=review to main"
    push_branch main

    log "--- $task_id done ---"
  done
}

# ── Stop condition ────────────────────────────────────────────────

should_stop() {
  if [ -f "$CTO_DIR/NO_TASKS" ]; then
    log "CTO signaled done: $(cat "$CTO_DIR/NO_TASKS")"
    return 0
  fi
  if [ "$CYCLE" -ge "$MAX_CYCLES" ]; then
    log "Reached max cycles ($MAX_CYCLES)."
    return 0
  fi
  return 1
}

# ── Main loop ─────────────────────────────────────────────────────

main() {
  log "Starting orchestrator. Repo: $REPO_ROOT"
  preflight

  while true; do
    CYCLE=$((CYCLE + 1))
    log "══════ Cycle $CYCLE ══════"

    run_cto_phase
    # Always process decisions — merges/closes must happen even if this is the last cycle
    process_cto_decisions
    should_stop && { log "Stopping."; break; }

    run_task_phase
    should_stop && { log "Stopping."; break; }

    log "Cycle $CYCLE complete."
  done

  log "Orchestrator finished after $CYCLE cycle(s)."
}

main "$@"
