# Lead State

Dynamic working memory. Updated by Lead each cycle.
Full decisions log: `lead/decisions.md` (newest first).

---

## Mandate

**Current focus: Topology Research Program v1**

Research question: Do different AI agent coordination topologies produce measurably different empirical outcomes when given an identical task?

Controlled task: **Debate Engine** (FastAPI + UI + tests) — built independently under each topology into its own subdirectory.

Phases: 0 (Instrument) → 1 (Broadcast) → 2 (Pipeline) → 3 (Adversarial) → 4 (Specialist) → 5 (Synthesis). 40+ cycles. Do not rush.

**Prior focus (complete):** Production-quality hardening — task-007/008/009 accepted 2026-03-01.

---

## Backlog

### Needs Human Input
<!-- Tasks or decisions blocked on human — describe exactly what's needed -->
*(none)*

### Planned
<!-- Priority order. Format: - [task-XXX] Description | P1/P2/P3 | deps: none -->
*(none)*

### Active
<!-- Format: - [task-XXX] Description | status | branch -->
- [task-011] BROADCAST Agent A: schema.md + api.py | assigned | task/011-broadcast-a-api
- [task-012] BROADCAST Agent B: ui.html | assigned | task/012-broadcast-b-ui
- [task-013] BROADCAST Agent C: tests/test_api.py | assigned | task/013-broadcast-c-tests

### Done (recent)
<!-- Keep last ~10. Format: - [task-XXX] Description | accepted/discarded | YYYY-MM-DD -->
- [task-010] Dashboard research panel | accepted | 2026-03-01
- [task-009] Repo cleanup + orchestrator re-processing fix | accepted | 2026-03-01
- [task-008] Architecture diagram | accepted | 2026-03-01
- [task-007] Fix orchestrator env vars + deploy dashboard to GitHub Pages | accepted | 2026-03-01
- [task-006] Restructure repo to three-domain architecture | accepted | 2026-03-01
- [task-005] Fix orchestrator merge gate (remove reviewDecision check) | accepted | 2026-03-01
- [task-004] Restructure repo to three-domain architecture | discarded (PR #1 closed, merge conflicts) | 2026-03-01
- [task-003] Org Progress Dashboard (single-file HTML, GitHub API) | accepted | 2026-03-01
- [task-002] Bookmark Manager REST API (Python/FastAPI) | accepted | 2026-03-01
- [task-001] Node.js REST API (items CRUD) | accepted | 2026-03-01

---

## Recent Decisions
<!-- Top 20 only — one line each. Full log in lead/decisions.md -->
<!-- Format: [YYYY-MM-DDTHH:MM] task-XXX ACTION — reason -->
- [2026-03-01T27:00] task-011/012/013 ASSIGNED — Phase 1 BROADCAST begins; all 3 agents simultaneous, isolated, writing to product/debate-engine/broadcast/
- [2026-03-01T27:00] task-010 ACCEPTED — all 6 criteria met; Phase 0 instrumentation complete; gh self-review blocked (single-author)
- [2026-03-01T26:00] MANDATE CHANGED — Topology Research Program v1; Phase 0 started; task-010 assigned (dashboard research panel); BROADCAST tasks planned
- [2026-03-01T25:00] task-007/008/009 ACCEPTED — all production hardening criteria met; accepted via branch diff (single-author)
- [2026-03-01T24:00] task-009 UPDATED — Problem 4 added to package.md: NO_TASKS robustness safeguard in orchestrator.sh main loop
- [2026-03-01T23:59] task-009 ASSIGNED — repo cleanup: archive task-001–004, fix orchestrator re-processing, remove lead/logs/build/
- [2026-03-01T23:59] task-008 ASSIGNED — create ARCHITECTURE.md with ASCII flow diagram and domain map
- [2026-03-01T23:59] task-007 ASSIGNED — fix orchestrator env var names, add GitHub Pages deploy job, set dashboard defaults
- [2026-03-01T23:55] task-006 ACCEPTED — all 8 criteria met; gh self-review blocked (single-author), accepted via branch diff; NO_TASKS written
- [2026-03-01T23:50] task-006 ASSIGNED — repo restructure re-run from main; PR #1 already closed, changes never landed
- [2026-03-01T23:45] LEAD CYCLE PASS — no tasks in review, backlog empty, NO_TASKS confirmed; awaiting next mandate
- [2026-03-01T23:30] task-005 ACCEPTED — all 6 criteria met; gh self-review blocked (known single-author limit), accepted via branch diff; NO_TASKS written
- [2026-03-01T23:00] task-005 ASSIGNED — fix orchestrator merge gate; remove reviewDecision check from orchestrator.sh; read from outbox.md direction
- [2026-03-01T22:00] task-004 ACCEPTED — all 9 criteria met; gh self-review blocked (known single-author limit), accepted via branch diff; NO_TASKS written
- [2026-03-01T21:00] task-004 ASSIGNED — repo restructure to three-domain architecture per Think outbox.md direction; NO_TASKS cleared
- [2026-03-01T20:00] LEAD CYCLE PASS — mandate complete, all tasks accepted, backlog empty; NO_TASKS written
- [2026-03-01T18:00] task-003 ACCEPTED — dashboard renders mandate, task board, decisions, cycle timeline; no PR (Think-mode session); accepted via direct diff
- [2026-02-28T12:00] MANDATE CHANGED — new mandate: Org Progress Dashboard (single-file HTML, GitHub API reads)
- [2026-02-28T12:00] task-003 ASSIGNED — build dashboard: mandate panel, task board, decisions feed, cycle timeline
- [2026-03-01T15:00] task-002 ACCEPTED — all 5 endpoints correct, AnyHttpUrl validation, tag filtering, pinned requirements.txt, README with curl examples; mandate complete
- [2026-03-01T13:00] task-002 ASSIGNED — implement Python/FastAPI bookmark manager (mandate not yet built)
- [2026-03-01T00:00] task-001 ASSIGNED — first task: bootstrap product context + implement full REST API (Express, in-memory)

---

## Research Log

### Phase 1: BROADCAST — 2026-03-01
**Hypotheses:** H1 under test: independent agents given identical context will converge on similar API contracts (field names, paths, status codes). H2 (pipeline will show tighter coupling) is the comparison baseline for next phase.
**Observations:** task-011/012/013 assigned simultaneously. Agents B (ui) and C (tests) explicitly instructed not to read Agent A's output. Each must document assumed API contract in a comment block — this is the primary measurement artifact. Product target: `product/debate-engine/broadcast/`.
**Surprises:** None yet — tasks just assigned.
**Next phase adaptation:** After all three are accepted, compare the three assumed API contracts: (1) schema.md vs. ui.html comment block — count matching endpoint paths, field names, status codes. (2) schema.md vs. test_api.py comment block — same comparison. Record alignment score. High alignment supports H1; low alignment refutes it.

### Phase 0: INSTRUMENT — 2026-03-01
**Hypotheses:** All 5 hypotheses (H1–H5) established. H1 and H2 will be tested in Phases 1 and 2. No empirical data yet.
**Observations:** Infrastructure setup cycle. Lead-direct actions completed: (1) Research Log section added to state.md, (2) topology/phase fields added to status.md template in lead/CLAUDE.md. Dashboard research panel task (task-010) assigned and accepted.
**Surprises:** None — Phase 0 is instrumentation only.
**Next phase adaptation:** Phase 1 BROADCAST (task-011/012/013) assigned simultaneously this cycle. Key watch: do task-012 (ui.html) and task-013 (tests) correctly predict task-011's API contract? Record specific field name / status code mismatches.
