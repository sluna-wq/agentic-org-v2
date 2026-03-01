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
- [task-015] PIPELINE Agent B: api.py (reads schema from task-014) | P1 | deps: task-014
- [task-016] PIPELINE Agent C: tests/test_api.py (reads schema + api from task-014/015) | P1 | deps: task-014, task-015

### Active
<!-- Format: - [task-XXX] Description | status | branch -->
- [task-014] PIPELINE Agent A: schema.md | assigned | task/014-pipeline-a-schema

### Done (recent)
<!-- Keep last ~10. Format: - [task-XXX] Description | accepted/discarded | YYYY-MM-DD -->
- [task-013] BROADCAST Agent C: tests/test_api.py | accepted | 2026-03-01
- [task-012] BROADCAST Agent B: ui.html | accepted | 2026-03-01
- [task-011] BROADCAST Agent A: schema.md + api.py | accepted | 2026-03-01
- [task-010] Dashboard research panel | accepted | 2026-03-01
- [task-009] Repo cleanup + orchestrator re-processing fix | accepted | 2026-03-01
- [task-008] Architecture diagram | accepted | 2026-03-01
- [task-007] Fix orchestrator env vars + deploy dashboard to GitHub Pages | accepted | 2026-03-01
- [task-006] Restructure repo to three-domain architecture | accepted | 2026-03-01
- [task-005] Fix orchestrator merge gate (remove reviewDecision check) | accepted | 2026-03-01
- [task-004] Restructure repo to three-domain architecture | discarded (PR #1 closed, merge conflicts) | 2026-03-01

---

## Recent Decisions
<!-- Top 20 only — one line each. Full log in lead/decisions.md -->
<!-- Format: [YYYY-MM-DDTHH:MM] task-XXX ACTION — reason -->
- [2026-03-01T28:00] task-014/015/016 ASSIGNED — Phase 2 PIPELINE; task-014 active, 015/016 planned (sequential deps)
- [2026-03-01T28:00] task-011/012/013 ACCEPTED — Phase 1 BROADCAST complete; H1 PARTIALLY REFUTED: B+C each diverged 2/5 dimensions but in different dimensions
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

---

## Research Log

### Phase 2: PIPELINE — 2026-03-01
**Hypotheses:** H2 under test: when agents read upstream output, they produce tighter contract coupling (higher alignment with the authoritative schema). Comparison baseline: BROADCAST alignment scores (B=2/5, C=2/5).
**Observations:** task-014 assigned (Agent A writes schema.md). task-015 and task-016 planned sequentially — 015 reads 014, 016 reads 014+015. This is the key controlled difference from BROADCAST: full upstream visibility.
**Surprises:** None yet — Phase 2 just assigned.
**Next phase adaptation:** After all three accepted, compare task-015's comment block and task-016's comment block against task-014's schema.md on the same 5 dimensions used in Phase 1. Score and compare to BROADCAST baseline.

### Phase 1: BROADCAST — 2026-03-01
**Hypotheses:** H1 under test: independent agents given identical context will converge on similar API contracts. RESULT: PARTIALLY REFUTED.
**Observations:** Contract divergence measured across 5 dimensions:
- Agent B (ui): matched field names (`topic`, `side`) but diverged on shapes (wrapped array, embedded arguments). Score: 2/5.
- Agent C (tests): matched shapes (bare array, separate endpoint) but diverged on field names (`title` not `topic`, `position` not `side`). Score: 2/5.
- B and C diverged from A in *complementary* dimensions — neither matched the other's pattern of error.
**Surprises:** B and C each scored identically (2/5) but diverged on *different* dimensions. This suggests field names and response shapes are independently variable — agents may anchor on different aspects of the same conceptual description. The description "side: for or against" was interpreted as `side` by B but `position` by C.
**Next phase adaptation:** Phase 2 PIPELINE will test H2 (upstream visibility → tighter coupling). Measurement: same 5 dimensions, same scoring.

### Phase 0: INSTRUMENT — 2026-03-01
**Hypotheses:** All 5 hypotheses (H1–H5) established. H1 and H2 will be tested in Phases 1 and 2. No empirical data yet.
**Observations:** Infrastructure setup cycle. Lead-direct actions completed: (1) Research Log section added to state.md, (2) topology/phase fields added to status.md template in lead/CLAUDE.md. Dashboard research panel task (task-010) assigned and accepted.
**Surprises:** None — Phase 0 is instrumentation only.
**Next phase adaptation:** Phase 1 BROADCAST (task-011/012/013) assigned simultaneously this cycle. Key watch: do task-012 (ui.html) and task-013 (tests) correctly predict task-011's API contract? Record specific field name / status code mismatches.
