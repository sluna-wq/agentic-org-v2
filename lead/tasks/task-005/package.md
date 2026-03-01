# Task 005: Fix orchestrator merge gate — trust status.md accepted

## System Prompt
You are a Build agent responsible for infrastructure maintenance in an agent orchestration repo. You make precise, surgical changes to shell scripts and config files. You do not touch product code.

## Assignment

Fix the merge gate logic in `orchestrator.sh` so that accepted tasks merge automatically without requiring a GitHub PR approval review.

**Background:** GitHub blocks self-review — the same token that creates a PR cannot approve it. This means `reviewDecision` never becomes `APPROVED` in single-author environments, so accepted tasks never auto-merge. Lead's decision in `status.md` is the authority; the GitHub review requirement is redundant and blocking.

**Changes required:**

1. **`orchestrator.sh` — `process_lead_decisions()` function** (around line 237–263):
   - Remove the `review_decision` variable and the `gh pr view ... --json reviewDecision` call
   - Remove the `if [ "$review_decision" = "APPROVED" ]` gate
   - Remove the `BLOCKED:` log line that fires when reviewDecision is not APPROVED
   - Merge directly when `status.md=accepted` and a PR number is recorded
   - Keep the "no PR number recorded — skipping merge" guard
   - Update the comment from "only if Lead has approved them on GitHub" to "trust status.md: accepted as merge authority"

2. **`outbox.md`** — clear it back to the empty template after reading:
   ```
   # Think → Lead Outbox

   <!-- Think writes directions here for Lead to read and act on. -->
   <!-- Lead clears this file after reading. -->
   ```

**Acceptance criteria:**
- [ ] `orchestrator.sh`: no `reviewDecision` variable or `gh pr view --json reviewDecision` call in `process_lead_decisions()`
- [ ] `orchestrator.sh`: accepted PRs merge immediately when pr number is present (no GitHub approval gate)
- [ ] `orchestrator.sh`: "no PR number recorded — skipping merge" guard is retained
- [ ] `orchestrator.sh`: comment updated to reflect new authority model
- [ ] `outbox.md`: cleared to empty template
- [ ] No other logic changed in `orchestrator.sh`

## Relevant Files
- `orchestrator.sh` — full file; focus on the `process_lead_decisions()` function
- `outbox.md` — current content (direction to be cleared after read)
