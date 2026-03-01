# Architecture

## Agent Roles

- **Think** — Strategic voice; talks to human, sets mandate, writes outbox.md
- **Lead** — Orchestrator; reviews tasks, assigns work, never implements
- **Build** — Implementer; writes code to product/, commits to branch
- **Orchestrator** — Shell driver; invokes agents, manages PRs and merges

## Full Cycle Flow

  ┌────────────────────────────────────────────────┐
  │  Think  (human ↔ Claude, interactive)          │
  │  sets mandate · writes outbox.md               │
  └─────────────────────┬──────────────────────────┘
                        │ outbox.md read every cycle
                        ▼
  ┌────────────────────────────────────────────────┐
  │  orchestrator.sh  (main loop)                  │
  └──────┬─────────────────────────────────────────┘
         │ Phase 1 — invoke Lead
         ▼
  ┌────────────────────────────────────────────────┐
  │  Lead                                          │
  │  · reads outbox.md → acts on directions        │
  │  · reviews "review" tasks → accept / discard   │
  │  · assigns tasks → lead/tasks/task-XXX/        │
  └──────┬─────────────────────────────────────────┘
         │ Phase 1b — process decisions
         ▼
  ┌────────────────────────────────────────────────┐
  │  orchestrator.sh                               │
  │  · squash-merges accepted PRs → main           │
  │  · closes discarded PRs                        │
  └──────┬─────────────────────────────────────────┘
         │ Phase 2 — invoke Build (one per task)
         ▼
  ┌────────────────────────────────────────────────┐
  │  Build                                         │
  │  · reads product/CLAUDE.md                     │
  │  · writes code to product/                     │
  │  · commits to branch · sets status=review      │
  └──────┬─────────────────────────────────────────┘
         │ push branch + open PR
         ▼
  ┌────────────────────────────────────────────────┐
  │  GitHub PR  (Lead reviews next cycle)          │
  └──────┬─────────────────────────────────────────┘
         │
         └──────────────────────────────── repeat ↑

## Domain Map

  lead/
  ├── CLAUDE.md       Lead agent instructions
  ├── state.md        Working memory: mandate, backlog, decisions
  ├── decisions.md    Full decisions log (newest first)
  ├── outbox.md       Inbox from Think; cleared after each read
  └── tasks/
      └── task-XXX/
          ├── package.md    Assignment brief
          ├── status.md     status · branch · PR number
          └── transcript.md Agent session log

  product/
  ├── CLAUDE.md       Build agent instructions + product context
  └── dashboard/
      ├── index.html  Org Progress Dashboard (single-file HTML app)
      └── README.md   Setup instructions

  logs/
  └── lead/
      └── cycle-N.md  Lead session transcripts (one per cycle)
