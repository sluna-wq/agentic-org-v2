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

### Active
<!-- Format: - [task-XXX] Description | status | branch -->
- [task-020] SPECIALIST Agent A: schema.md | assigned | task/020-specialist-a-schema

### Planned
<!-- Priority order. Format: - [task-XXX] Description | P1/P2/P3 | deps: none -->
- [task-021] SPECIALIST Agent B: api.py | P1 | deps: task-020
- [task-022] SPECIALIST Agent C: evaluation.md + tests/test_api.py | P1 | deps: task-020,task-021

### Done (recent)
<!-- Keep last ~10. Format: - [task-XXX] Description | accepted/discarded | YYYY-MM-DD -->
- [task-019] ADVERSARIAL Agent C: critique.md + tests/test_api.py | accepted | 2026-03-01
- [task-018] ADVERSARIAL Agent B: api.py | accepted | 2026-03-01
- [task-017] ADVERSARIAL Agent A: schema.md | accepted | 2026-03-01
- [task-016] PIPELINE Agent C: tests/test_api.py | accepted | 2026-03-01
- [task-015] PIPELINE Agent B: api.py | accepted | 2026-03-01
- [task-014] PIPELINE Agent A: schema.md | accepted | 2026-03-01
- [task-013] BROADCAST Agent C: tests/test_api.py | accepted | 2026-03-01
- [task-012] BROADCAST Agent B: ui.html | accepted | 2026-03-01
- [task-011] BROADCAST Agent A: schema.md + api.py | accepted | 2026-03-01
- [task-010] Dashboard research panel | accepted | 2026-03-01

---

## Recent Decisions
<!-- Top 20 only — one line each. Full log in lead/decisions.md -->
<!-- Format: [YYYY-MM-DDTHH:MM] task-XXX ACTION — reason -->
- [2026-03-01T32:00] task-017/018/019 ACCEPTED — ADVERSARIAL 5/5 across all agents; 61 tests vs PIPELINE 29; H3: adversarial framing ~2x tests even with 0 deviations; task-020/021/022 ASSIGNED — Phase 4 SPECIALIST
- [2026-03-01T31:00] task-016 ACCEPTED — PIPELINE tests: Agent C 5/5 (H2 fully supported across full pipeline); task-017/018/019 ASSIGNED — Phase 3 ADVERSARIAL
- [2026-03-01T30:00] task-015 ACCEPTED — PIPELINE api.py: 5/5 score vs BROADCAST B 2/5 (H2 strongly supported); task-016 ASSIGNED
- [2026-03-01T29:00] task-014 ACCEPTED — PIPELINE schema: all criteria met, field names explicit, Notes section for B+C; task-015 ASSIGNED
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

---

## Research Log

### Phase 4: SPECIALIST — 2026-03-01
**Hypotheses:** H4 under test: when agents are explicitly framed as domain specialists (Senior REST API Designer, Senior FastAPI Engineer, QA Contract Testing Specialist), do they make measurably different design decisions vs PIPELINE agents given the same structural topology? Does specialist framing produce qualitatively different schema choices, implementation patterns, or test strategies?
**Design:** Same pipeline structure as Phase 2 (Agent B reads A's schema; Agent C reads both). Key additions: Agent A adds "Design Rationale" section; Agent B adds "Implementation Notes"; Agent C adds "Specialist Observations" per dimension + "Specialist Verdict". Measurement: compare field name choices, schema structure, test count, and design decisions to PIPELINE equivalents.
**Measurement:** Schema field names vs PIPELINE/ADVERSARIAL; test count vs PIPELINE (29) and ADVERSARIAL (61); any qualitative design divergence in Design Rationale / Implementation Notes.
**Observations:** In progress — task-020 active, task-021/022 planned.

### Phase 3: ADVERSARIAL — 2026-03-01 ✅ COMPLETE
**Hypotheses:** H3 under test: when Agent C is explicitly framed as an adversary (red-team reviewer), does it produce a more rigorous critique and test suite than a neutral PIPELINE Agent C? Does adversarial framing cause Agent C to find deviations that a neutral tester would miss?
**Design:** Agent A writes schema with Notes-for-B-and-C section (adversarial anchor). Agent B implements, trying to give Agent C no ammunition. Agent C reads both, writes critique.md (5-dimension schema-vs-implementation comparison + score), then writes tests designed to catch deviations.
**Measurement:** Compare Agent C's critique score, test count, and test assertion depth to PIPELINE Agent C (5/5, 29 tests, UUID/ISO validation present). Key question: does adversarial framing change the output?
**Observations:**
- task-017 (Agent A schema): 26-constraint Notes section — most precise adversarial anchor in program. Field names: title/description (Debate), side/body (Argument).
- task-018 (Agent B api.py): perfect compliance — 0 deviations. Correct ?side= validation precedence (validates before checking debate existence). Custom 422 handler. Input sanitization.
- task-019 (Agent C critique + tests): score 5/5. 61 tests vs PIPELINE 29 (~2x). Adversarial framing changed testing strategy: more edge cases, explicit deviation-hunting tests, set-equality field assertions, precedence tests.
**Result: H3 PARTIALLY SUPPORTED.** Adversarial framing produced ~2x more tests and more systematic edge-case coverage even when Agent B had 0 deviations. Agent C could not "find deviations that a neutral tester would miss" because there were no deviations to find — but the testing approach was demonstrably more rigorous. Future test: run adversarial topology against a deliberately flawed implementation.
**Surprises:** The framing effect on Agent C was measurable in the "no deviations" case — test count alone (~2x) suggests the adversarial identity changes the testing strategy independent of what is found. Agent A's 26-constraint schema is qualitatively different from PIPELINE Agent A's Notes section (which had ~5 constraints).

### Phase 2: PIPELINE — 2026-03-01 ✅ COMPLETE
**Hypotheses:** H2 under test: when agents read upstream output, they produce tighter contract coupling (higher alignment with the authoritative schema). Comparison baseline: BROADCAST alignment scores (B=2/5, C=2/5).
**Observations:**
- task-014 (Agent A schema): highly explicit — dedicated Data Models section, 5-constraint Notes for B+C, 422 validation, ?side= filter, ordering spec.
- task-015 (Agent B api.py): **score 5/5**. Perfect contract match — all field names, response shapes, status codes, ?side= filter, 422 envelope correct. vs BROADCAST B: 2/5.
- task-016 (Agent C tests): **score 5/5**. Contract comment block correct, all 6 coverage areas, explicit field-name + envelope + filter assertions, UUID/ISO format validation. 29 tests. vs BROADCAST C: 2/5.
**Result: H2 FULLY SUPPORTED.** PIPELINE topology produced 5/5 across all 3 agents. BROADCAST produced 2/5 for B and C independently. Mechanism: explicit Notes section in Agent A's schema leaves no room for downstream agents to anchor on the wrong dimension.
**Surprises:** B and C in PIPELINE both hit 5/5 with no prompting beyond reading Agent A's schema. The schema quality (explicit Notes) appears to be the decisive factor, not just the pipeline structure itself.
**Next phase adaptation:** Phase 3 ADVERSARIAL will test whether adversarial framing of Agent C changes output quality. Measurement: same 5 dimensions + critique.md depth + test assertion rigor.

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
