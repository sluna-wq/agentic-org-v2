# Task 008: Architecture diagram

## System Prompt

You are a Build agent creating documentation for this agentic repo. You will create a single crisp architecture document at the repo root showing the full system flow and domain map.

**Write access for this task:**
- `ARCHITECTURE.md` (create at repo root)
- Your own `lead/tasks/task-008/status.md`

## Assignment

Create `ARCHITECTURE.md` at the repo root. One page, crisp ASCII art. Max 80 chars wide. No prose paragraphs beyond one-liners. Under 120 lines total.

### Required sections

**1. Flow diagram** — ASCII showing the full cycle:
```
Think (human + Claude) → writes outbox.md
→ orchestrator.sh invokes Lead (Claude)
→ Lead writes task packages to lead/tasks/
→ orchestrator invokes Build (Claude)
→ Build commits to branch
→ orchestrator opens PR
→ Lead reviews PR
→ orchestrator merges
→ main updated
```

Make it look like a real flow diagram with boxes/arrows. Keep it elegant.

**2. Domain map** — what lives in each of the three domains:
- `lead/` — state.md, decisions.md, tasks/, outbox.md
- `product/` — all built artifacts (APIs, dashboard, etc.)
- `logs/` — transcripts (logs/lead/ for lead cycle logs)

**3. Agent role descriptions** — one sentence each:
- **Think** — strategic voice; talks to human, sets mandate, writes to outbox.md
- **Lead** — orchestrates; reviews tasks, assigns work, never implements
- **Build** — implements; writes code to product/, commits to branch
- **Orchestrator** — shell driver; invokes agents, manages PRs and merges

### Acceptance criteria
- [ ] File exists at `ARCHITECTURE.md`
- [ ] Has a readable ASCII flow diagram covering the full cycle
- [ ] Has the three-domain map
- [ ] Has one-sentence agent descriptions
- [ ] Under 120 lines total
- [ ] Max 80 chars wide

## Relevant Files

- `CLAUDE.md` — read for accurate mode descriptions
- `orchestrator.sh` — read to understand what the orchestrator actually does
- `lead/state.md` — read for current mandate context
