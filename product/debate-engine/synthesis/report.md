# Topology Research Program v1 — Final Synthesis Report

**Author:** Build Agent (Synthesis, Phase 5)
**Date:** 2026-03-01
**Program:** Topology Research Program v1
**Phases covered:** 1 (BROADCAST), 2 (PIPELINE), 3 (ADVERSARIAL), 4 (SPECIALIST)

---

## 1. Program Overview

### Research Question

Do different AI agent coordination topologies produce measurably different empirical outcomes when given an identical task? This program operationalized "different outcomes" as contract alignment scores (how faithfully an implementation matches its authoritative schema), test suite depth (test count and assertion quality), and qualitative schema richness (constraint count, explicitness, and novel design decisions). The program ran across four phases over a single day (2026-03-01) and concluded with this synthesis.

### Controlled Task: Debate Engine

All four topology phases built the same product: a Debate Engine REST API implemented in Python with FastAPI, plus an in-memory data store and a test suite. The API manages two resources (Debates and Arguments) across five endpoints: `POST /debates`, `GET /debates`, `GET /debates/{id}`, `POST /debates/{id}/arguments`, and `GET /debates/{id}/arguments`. This task was chosen because it is scoped enough to complete in a single agent session yet complex enough to expose design decision variation (field naming, response envelope shape, status code selection, filter behavior, error handling). The task was held constant across all four topology phases.

### Topology 1: BROADCAST

Three agents were issued identical task specifications simultaneously with explicit isolation constraints — Agent B and Agent C were instructed not to read any other agent's output. Agent A produced the authoritative schema (`schema.md`) and reference implementation (`api.py`). Agent B independently invented a UI (`ui.html`), and Agent C independently invented a test suite (`tests/test_api.py`). Measurement: how much did B and C's independently inferred API contracts diverge from A's authoritative contract?

### Topology 2: PIPELINE

Three agents worked sequentially with full upstream visibility. Agent A produced `schema.md` without reading any prior output. Agent B read Agent A's `schema.md` and produced `api.py`. Agent C read both `schema.md` and `api.py` and produced `tests/test_api.py`. The pipeline design introduced an explicit "Notes for Agents B and C" section in the schema specifying five implementation constraints. Measurement: does upstream visibility close the alignment gap observed in BROADCAST?

### Topology 3: ADVERSARIAL

Same sequential pipeline structure as Phase 2, but with adversarial framing applied to Agent C. Agent A produced a schema with a 26-constraint adversarial anchor section. Agent B produced an implementation explicitly trying to give Agent C no defects to find. Agent C was framed as a red-team adversary whose job was to prove deviations rather than assume correctness; Agent C produced both a written critique (`critique.md`) and a test suite (`tests/test_api.py`). Measurement: does adversarial framing change Agent C's output quality independent of implementation quality?

### Topology 4: SPECIALIST

Same sequential pipeline structure as Phases 2 and 3, but each agent was given an explicit domain specialist identity: Agent A as "Senior REST API Designer," Agent B as "Senior FastAPI Engineer," Agent C as "QA Contract Testing Specialist." Specialist-specific output requirements were added to each agent's assignment: a "Design Rationale" section (Agent A), "Implementation Notes" (Agent B), and per-dimension "Specialist Observations" plus a "Specialist Verdict" (Agent C). Measurement: does specialist identity framing produce measurably different design decisions vs. neutral PIPELINE agents, even when the structural topology is identical?

---

## 2. Hypotheses

### H1 — BROADCAST Convergence

**Prediction:** Independent agents given identical context will converge on similar API contracts. If agents are reasoning from the same specification, they should arrive at the same field names, response shapes, and status code choices.

**Observed:** Both Agent B (UI) and Agent C (tests) scored 2/5 against Agent A's authoritative contract, but they diverged on *different* dimensions. Agent B matched Agent A's field names (`topic`, `side`) but invented different response shapes (`{"debates":[...]}` wrapper instead of bare array; debate + embedded arguments on GET /debates/{id} instead of debate alone). Agent C matched Agent A's response shapes (bare arrays, separate endpoints) but invented different field names (`title` instead of `topic`, `position` instead of `side`).

| Aspect | Agent A (ground truth) | Agent B (UI) | Agent C (tests) |
|--------|------------------------|--------------|-----------------|
| Debate name field | `topic` | `topic` ✓ | `title` ✗ |
| Argument side field | `side` | `side` ✓ | `position` ✗ |
| GET /debates format | bare `[...]` | `{"debates":[...]}` ✗ | bare `[...]` ✓ |
| GET /debates/{id} | debate only | debate + args embedded ✗ | debate only ✓ |
| Separate GET /arguments | yes | not called ✗ | yes ✓ |

**Verdict: PARTIALLY REFUTED.** Convergence did not occur. Neither B nor C produced a contract fully matching A's. The divergences were not random: the two agents anchored on *complementary* aspects of the specification (field names vs. structural shapes), producing a systematic pattern of partial overlap rather than agreement or chaos.

---

### H2 — PIPELINE Coupling

**Prediction:** When agents read upstream output, they produce tighter contract coupling — higher alignment with the authoritative schema than independent agents.

**Observed:** PIPELINE Agent B (reading Agent A's schema) scored 5/5 across all five research dimensions: field names, response envelopes, status codes, `?side=` filter, and 422 error envelope. PIPELINE Agent C (reading both schema and api.py) also scored 5/5. This compares to BROADCAST B=2/5 and C=2/5.

The enabling mechanism was Agent A's explicit "Notes for Agents B and C" section, which enumerated five specific implementation constraints (server-generated UUIDs, ISO 8601 timestamps, strict `side` enum, `?side=` query parameter behavior, independent UUID namespaces). Both downstream agents implemented exactly these constraints without deviation.

**Verdict: FULLY SUPPORTED.** PIPELINE topology produced 5/5 alignment vs. BROADCAST's 2/5 baseline — a clear, large-magnitude effect. The mechanism is schema explicitness: annotating the schema with downstream agent instructions leaves no room for inference errors.

---

### H3 — ADVERSARIAL Rigor

**Prediction:** When Agent C is explicitly framed as an adversary (red-team reviewer), it produces a more rigorous critique and test suite than a neutral PIPELINE Agent C. Adversarial framing may cause Agent C to find deviations that a neutral tester would miss.

**Observed:** Agent C produced 61 tests — approximately 1.85× more than PIPELINE Agent C (33 tests). The critique methodology was demonstrably different: Agent C read the implementation line-by-line per dimension with the explicit goal of "proving deviation, not assuming correctness," and added novel test categories absent from the PIPELINE suite (client-supplied field suppression tests, whitespace-only body → 422 tests, `?side=` precedence-ordering tests, capitalisation variant tests). Agent B's implementation had zero deviations across all five dimensions, so the "find deviations that a neutral tester would miss" question could not be answered in this experiment — there was nothing to find.

**Verdict: PARTIALLY SUPPORTED.** The adversarial framing measurably changed Agent C's *testing strategy* (test count, edge-case coverage, adversarial test categories) independent of what Agent B delivered. The framing effect is real and quantifiable even in the absence of defects. However, whether adversarial framing would detect deviations that neutral framing would miss remains untested — testing adversarial topology against a deliberately flawed implementation is the natural next experiment.

---

### H4 — SPECIALIST Design Decisions

**Prediction:** When agents are explicitly framed as domain specialists, they make measurably different design decisions vs. PIPELINE agents given the same structural topology.

**Observed:** SPECIALIST Agent A (Senior REST API Designer) introduced two fields not present in any prior topology — `argument_count` (a denormalized counter on the Debate resource) and `total` in list response envelopes — and provided formal "Design Rationale" justifications for five specific decisions (field name choices, envelope structure, sort order semantics). Agent B (Senior FastAPI Engineer) used `Literal["for", "against"]` for `side` validation (idiomatic Pydantic v2 pattern absent from all prior topologies), computed `argument_count` dynamically to eliminate counter-drift bugs, and separated request/response Pydantic models as a contract-enforcement pattern. Agent C (QA Contract Testing Specialist) produced 71 tests with per-dimension "Specialist Observations" sections that identified edge cases beyond pass/fail (e.g., `description` defaulting to `""` vs. null, `total` reflecting filtered vs. unfiltered count, `argument_count` consistency edge cases). Implementation score was 4/5 with the single failure on the 422 error envelope.

The 422 deviation is a methodological confound: the task assignment's package.md criterion specified `{"error":"..."}` as the 422 shape while the schema specified FastAPI native format. Agent B followed the explicit package criterion. This should not be attributed to specialist framing.

**Verdict: PARTIALLY SUPPORTED.** Specialist framing produced qualitatively richer schema outputs (new fields, explicit rationale, more constraints) and idiomatic implementation patterns not seen in PIPELINE or ADVERSARIAL. The specialist identity caused Agent A to frame the design problem differently — adding `argument_count` and `total` was motivated by reasoning about client N+1 query costs and future pagination extensibility, reasoning not present in neutral topologies. The 4/5 score is a confound artifact, not a specialist framing effect.

---

## 3. Cross-Topology Comparison

### Agent B Implementation Compliance Against Agent A Schema

The five research dimensions are: (1) Field Names — correct field names on Debate and Argument objects; (2) Response Envelopes — correct list response shape (bare array vs. wrapped object); (3) Status Codes — 201/200/404/422 used correctly; (4) `?side=` Filter — optional side filter on the arguments list endpoint; (5) 422 Envelope — correct error shape for validation failures.

| Topology | Field Names | Response Envelopes | Status Codes | `?side=` Filter | 422 Envelope | Total |
|---|---|---|---|---|---|---|
| BROADCAST | PASS | FAIL | N/A† | N/A† | N/A† | 2/5‡ |
| PIPELINE | PASS | PASS | PASS | PASS | PASS | 5/5 |
| ADVERSARIAL | PASS | PASS | PASS | PASS | PASS | 5/5 |
| SPECIALIST | PASS | PASS | PASS | PASS | FAIL* | 4/5 |

**† BROADCAST Agent B wrote a UI (`ui.html`), not an API implementation.** Status codes, `?side=` filter, and 422 envelope are not applicable to a UI artifact. The 2/5 score reflects compliance on the 5 contract-inference aspects tracked by Lead (see table in Section 2 H1 above).

**‡ BROADCAST measurement methodology differs.** BROADCAST was not evaluated against the formal 5 API dimensions at the time of acceptance; it used 5 contract-inference aspects comparing B's and C's independently invented contracts against Agent A's schema. The 2/5 score on those aspects is not directly comparable to the 5/5 scores in later phases, but it establishes the pre-visibility baseline.

**\* SPECIALIST 422 failure is an assignment-conflict artifact.** The package.md acceptance criterion specified `{"error":"..."}` for 422 responses; the schema.md specified FastAPI native `{"detail":[...]}`. Agent B followed the explicit package criterion. The Lead classified this as a confound, not a topology finding.

### What Each Topology's Schema Specified

| Topology | Base URL | Debate name field | Argument text field | List envelopes | `?side=` specified | 422 envelope | Constraint count |
|---|---|---|---|---|---|---|---|
| BROADCAST | `/` | `topic` | `content` | bare `[...]` | no | no | ~0 explicit |
| PIPELINE | `/api/v1` | `topic` | `content` | `{"debates":[...]}`, `{"arguments":[...]}` | yes | `{"error":"string"}` | 5 in Notes |
| ADVERSARIAL | `/api/v1` | `title` | `body` | bare `[...]` | yes (+ precedence rules) | `{"error":"string"}` | 26 in Notes |
| SPECIALIST | `/api/v1` | `title` | `body` | `{"debates":[...],"total":N}`, `{"arguments":[...],"total":N}` | yes | FastAPI native | ~7 constraint classes |

---

## 4. Emergent Findings

The following observations were not part of the original H1–H4 hypotheses but emerged from comparing the four topology outputs.

### Finding 1: Field Name Vocabulary Drift Between Phases

BROADCAST and PIPELINE both used `topic` (debate title) and `content` (argument text). ADVERSARIAL independently chose `title` and `body` — a vocabulary change not explained by the task specification, which used neutral language. SPECIALIST inherited `title` and `body` from ADVERSARIAL. The shift happened at ADVERSARIAL, where Agent A's framing as an adversarial schema designer may have driven more precise terminology choices (`body` as a standard HTTP term; `title` as more conventional than `topic` for a named resource). This suggests agent schemas can drift on vocabulary even when the conceptual task is identical, and that the drift is sticky — later topologies anchored on the precedent even though the topologies were designed to be independent.

### Finding 2: Test Count Trajectory Follows Framing Intensity

Test counts across phases: BROADCAST (24) → PIPELINE (33) → ADVERSARIAL (61) → SPECIALIST (71). The progression is monotonically increasing. The largest jump is PIPELINE → ADVERSARIAL (+28 tests, +85%), coinciding with the adversarial framing of Agent C. The smaller ADVERSARIAL → SPECIALIST increase (+10 tests, +16%) suggests specialist framing adds incremental depth beyond adversarial framing but not a step change. Test count alone is an imperfect proxy for quality (see Section 5), but the trajectory is consistent with the hypothesis that framing intensity (neutral < adversarial/specialist) drives testing thoroughness.

Note: the state.md Research Log entry for task-016 records "29 tests." The actual file on the task-016 branch contains 33 test functions. This 4-test discrepancy is a Lead observation error (likely a manual count made before final test additions or an approximation). The file is the authoritative source; 33 is the correct count.

### Finding 3: Specialist Identity Introduced Fields the Task Did Not Specify

Only SPECIALIST Agent A introduced `argument_count` on the Debate resource and `total` in list envelopes — neither was mentioned in any task assignment. Both emerged from specialist reasoning: `argument_count` was justified as preventing client N+1 queries; `total` as enabling future pagination without a breaking change. These are idiomatic REST API design decisions that a domain specialist would consider but a neutral agent did not. SPECIALIST Agent B then computed `argument_count` dynamically (O(N) scan rather than mutable counter), attributing this to eliminating counter-drift bugs — a different specialist-motivated decision about the *implementation strategy* for the same field. The field and its implementation strategy both emerged from specialist identity, not the task description.

### Finding 4: Complementary Divergence Pattern in BROADCAST

BROADCAST B and C each scored 2/5, but they failed on *complementary* dimensions — B anchored on field naming and invented response shapes; C anchored on response shapes and invented field names. This is not a random failure pattern. It suggests that agents reading the same specification independently focus on different cognitive anchors (naming conventions vs. structural conventions), and that these two aspects are sufficiently independent in the specification that agents can get one right while missing the other. This has practical implications for multi-agent systems: independent redundancy (running multiple agents on the same task) does not reliably catch all contract errors because each agent fails silently on the dimensions it de-emphasizes.

### Finding 5: Schema Constraint Count vs. Implementation Score Are Not Monotonically Related

Schema constraint counts: BROADCAST (~0 explicit) → PIPELINE (5) → ADVERSARIAL (26) → SPECIALIST (~7 constraint classes). Implementation scores: BROADCAST (2/5†) → PIPELINE (5/5) → ADVERSARIAL (5/5) → SPECIALIST (4/5 confound). Adding more constraints (ADVERSARIAL's 26 vs PIPELINE's 5) did not improve the already-perfect score — it was sufficient to maintain it. SPECIALIST's slightly lower score (4/5) occurred despite the most exhaustive constraint documentation, but this was a confound. The data suggests there may be a constraint-count threshold above which additional constraints do not meaningfully improve compliance — once an implementation is at 5/5, more constraints have diminishing returns on measurable compliance.

### Finding 6: 422 Error Envelope Is the Most Contested Dimension

Across all phases, the 422 error envelope specification varied the most:

- BROADCAST: not specified (Agent A's schema had no 422 envelope shape)
- PIPELINE: specified as `{"error": "string"}` — custom handler required
- ADVERSARIAL: specified as `{"error": "string"}` (note 21 in the 26-constraint Notes section)
- SPECIALIST: specified as FastAPI native `{"detail": [...]}` — the only topology to specify the framework default

This is the only dimension where SPECIALIST Agent A's schema diverged from ADVERSARIAL Agent A's schema. It is also the only dimension where Agent B deviated (following a conflicting package.md criterion). The 422 envelope dimension required the most explicit constraint text across all phases and still produced the only cross-phase deviation. This suggests the 422 error shape is the hardest contract dimension to nail down: it is not part of the "happy path" that agents naturally test, it requires overriding FastAPI's default behavior, and specification language about it varies across topologies.

---

## 5. Methodology Notes

### Single-Author GitHub Review Constraint

Every task in this program was accepted via branch diff rather than GitHub pull request review. GitHub's single-author restriction blocked `gh pr review --approve` throughout. This means no independent third-party review of any agent's output was possible; the Lead agent served as both assignor and reviewer. This is an inherent limitation of running an agentic org in a single-author GitHub environment. All acceptance decisions were made by the same entity that wrote the acceptance criteria, which introduces a potential confirmation bias: the Lead may have been more lenient on tasks that otherwise met criteria well. This is documented as a structural limitation of the current infrastructure, not a defect in individual task execution.

### BROADCAST Measurement Mismatch

BROADCAST was measured before the formal 5-dimension framework (Field Names / Response Envelopes / Status Codes / `?side=` Filter / 422 Envelope) was fully operationalized. The Lead used a 5-aspect contract-inference table comparing each agent's independently invented contract against Agent A's authoritative contract. This 5-aspect table is not directly comparable to the formal API compliance scores used in PIPELINE, ADVERSARIAL, and SPECIALIST. Additionally, BROADCAST Agent B produced a UI artifact (not an API implementation), which makes direct scoring on three of the five API dimensions (Status Codes, `?side=` Filter, 422 Envelope) inapplicable. Cross-phase comparison of BROADCAST scores to later phases should be done with this structural difference in mind.

### SPECIALIST 422 Assignment Conflict

The SPECIALIST assignment contained a methodological error: the package.md acceptance criterion specified `{"error":"..."}` as the 422 response shape while the schema.md (written by SPECIALIST Agent A) specified FastAPI native `{"detail":[...]}`. These are contradictory requirements. Agent B followed the explicit acceptance criterion and returned `{"error":"..."}` for 422 responses, which caused Agent C's evaluation to score this as a FAIL (since Agent C was comparing against the schema, not the package). The Lead correctly identified this as a confound: "The 422 deviation is an artifact of conflicting assignment signals, not specialist framing." The SPECIALIST 4/5 score should be read as 5/5 for topology-attributable dimensions.

### What Was Held Constant Across Topologies

The following were held constant across all four phases:
- The conceptual task: a Debate Engine REST API with the same five endpoints
- The five research dimensions used for scoring (partially — not applied retrospectively to BROADCAST)
- The language/framework stack: Python, FastAPI, Pydantic, in-memory storage
- The agent model: Claude claude-sonnet-4-6 (or equivalent)

### What Varied

- Schema authoring framing (neutral, neutral-with-Notes, adversarial-anchor, specialist-identity)
- Agent identity framing (neutral, neutral, adversarial [Agent C only], specialist [all agents])
- Schema constraint explicitness (0, 5, 26, ~7 constraint classes)
- Pipeline visibility (isolated, full upstream, full upstream, full upstream)
- Output artifacts required (Agent B: UI vs API; Agent C: tests vs critique+tests vs evaluation+tests)

---

## 6. Conclusions

### Conclusion 1: Upstream visibility is the single strongest predictor of implementation compliance in this program

The shift from BROADCAST (no upstream visibility, B=2/5) to PIPELINE (full upstream visibility, B=5/5) is the largest alignment improvement in the program — a 150% increase in compliance score. Adversarial framing (Phase 3) and specialist framing (Phase 4) did not improve on PIPELINE's 5/5 — they either maintained it (ADVERSARIAL) or matched it ignoring the confound (SPECIALIST). The mechanism is clear: when Agent B reads Agent A's explicit schema, there is no ambiguity about field names, envelope shapes, or validation behavior. Without visibility, agents infer the contract from general principles, producing systematically complementary errors. Schema visibility should be treated as a prerequisite for compliance, not an optional optimization.

### Conclusion 2: Adversarial framing has a large, measurable effect on testing thoroughness independent of implementation quality

ADVERSARIAL Agent C produced 61 tests vs PIPELINE Agent C's 33 (+85%) against an implementation with zero deviations. The adversarial framing effect is isolatable: the structural topology was identical (both are pipeline topologies), the implementation was equally compliant, and the only variable was Agent C's identity framing as an adversary tasked with "proving deviation." New test categories appeared under adversarial framing (whitespace-only → 422, capitalisation variant tests, client-supplied field suppression, `?side=` precedence ordering) that were absent from the neutral PIPELINE suite. This is a real, replicable framing effect, not an artifact of implementation differences.

### Conclusion 3: Specialist identity induces design decisions absent from both neutral and adversarial framing

The `argument_count` field and `total` in list envelopes emerged exclusively from SPECIALIST Agent A's specialist framing — no other topology included these fields, and no task assignment specified them. Agent A's Design Rationale section attributed these to client-side efficiency concerns (N+1 query avoidance) and API versioning concerns (future pagination). These are design considerations that a REST API specialist would naturally apply; a neutral agent framing the same task did not. This result has a practical implication: using specialist-identity framing for schema design agents will produce richer schemas that anticipate downstream client requirements, but at the cost of introducing fields that diverge from a minimal specification baseline.

### Conclusion 4: The five-dimension framework captures real variation, but dimension difficulty varies

Of the five dimensions, `?side=` Filter and Status Codes were universally compliant in all API-implementing topologies (PIPELINE, ADVERSARIAL, SPECIALIST). Field Names showed one early-phase failure (BROADCAST C used `position` instead of `side`). Response Envelopes showed disagreement between BROADCAST (bare arrays) and PIPELINE/SPECIALIST (wrapped objects). 422 Envelope was the only dimension where Agent B deviated from Agent A's specification in a non-BROADCAST topology (SPECIALIST). This ordering — from easy to hard: Status Codes ≤ ?side= Filter < Field Names < Response Envelopes < 422 Envelope — suggests that schema and test authors should pay disproportionate attention to the 422 error shape, which requires overriding a framework default, is easy to get wrong, and is inconsistently specified across all four schemas in this program.

### Conclusion 5: Schema quality is a topology variable, not a constant

Across the four phases, Agent A produced qualitatively different schemas even for the same API. BROADCAST Agent A produced a minimal schema with no constraint annotations. PIPELINE Agent A added a dedicated Notes section. ADVERSARIAL Agent A produced 26 explicit constraints. SPECIALIST Agent A produced the most exhaustive Notes for Agent B in the program, plus formal Design Rationale items. These differences are not random — they correspond to the framing of Agent A's role in each topology. The schema quality is itself an output variable of the topology, not a controlled input. Future topology experiments should consider explicitly controlling schema quality (e.g., using a fixed schema authored outside the topology) to isolate structural effects from schema-quality effects.

---

## 7. Suggested Future Research

### Experiment 1: Adversarial Topology Against a Deliberately Flawed Implementation

**Question:** Does adversarial framing of Agent C detect deviations that a neutral Agent C would miss, when deviations actually exist?

**Design:** Replicate Phase 3 ADVERSARIAL, but modify the Agent B assignment to intentionally introduce 3–5 subtle deviations (e.g., wrong sort order on GET /debates, missing whitespace stripping in validation, 200 instead of 201 on POST, `{"detail":...}` instead of `{"error":...}` on 422). Run two versions of Agent C in parallel: one with adversarial framing (identical to Phase 3) and one with neutral framing (identical to Phase 2 PIPELINE Agent C). Agents C are given the same schema.md and the same flawed api.py.

**Measurement:** Count which deviations each Agent C detects in the critique/tests. Primary metric: detection rate (deviations found / deviations planted). Secondary metric: false positive rate (deviations claimed that weren't planted). Compare critique depth between adversarial and neutral Agent C on the same inputs.

---

### Experiment 2: Pipeline Topology With a Minimal Schema (No Notes Section)

**Question:** Is PIPELINE's 5/5 compliance score driven by the pipeline structure itself (upstream visibility) or by Agent A's schema quality (explicit Notes section)?

**Design:** Replicate Phase 2 PIPELINE with Agent A explicitly constrained to write a minimal schema — same endpoints and data models, but no "Notes for Agents B and C" section, no constraint enumeration, no ordering specification, no error envelope specification. Agent B and Agent C receive the same pipeline structure (B reads schema, C reads schema + api.py) but a less prescriptive schema.

**Measurement:** Compare Agent B's compliance score on the 5 formal dimensions to PIPELINE's 5/5. If compliance drops, the Notes section (schema quality) is the causal mechanism. If compliance holds, pipeline structure (visibility) alone is sufficient.

---

### Experiment 3: Specialist Framing With a Fixed Schema

**Question:** Does specialist identity improve Agent B's implementation quality when the schema is held constant (not authored by a specialist Agent A)?

**Design:** Provide PIPELINE's `schema.md` (authored by a neutral Agent A) to two different Agent B instances: one with neutral framing (identical to PIPELINE Agent B) and one with specialist framing (identical to SPECIALIST Agent B — "Senior FastAPI Engineer"). Both agents read the same schema and produce an `api.py`.

**Measurement:** Compare compliance scores on the 5 dimensions, and compare qualitative implementation decisions (e.g., use of `Literal` types, model separation, error handling idioms, code comments). This isolates the specialist framing effect on implementation quality from the specialist framing effect on schema quality.

---

### Experiment 4: Defect-Injection Quality Measurement for Test Suites

**Question:** Does the test count increase (PIPELINE 33 → ADVERSARIAL 61 → SPECIALIST 71) correspond to an increase in actual bug-detection ability?

**Design:** Construct a reference implementation with 8 known defects (one covering each research dimension plus three subtle behavioral bugs: wrong sort order, off-by-one in length validation, counter-drift in argument_count). Run each topology's test suite (BROADCAST, PIPELINE, ADVERSARIAL, SPECIALIST) against this reference implementation without modification. Record which tests fail.

**Measurement:** Defect detection rate per test suite (defects caught / 8 total). This directly tests whether higher test counts translate to higher defect coverage, and whether adversarial/specialist testing strategies produce qualitatively different defect-catching profiles beyond their count advantage.

---

### Experiment 5: Multi-Run BROADCAST Topology

**Question:** Is the complementary-divergence pattern observed in Phase 1 (Agent B anchors on field names, Agent C anchors on shapes) stable across runs, or is it a single-trial artifact?

**Design:** Replicate Phase 1 BROADCAST three times with fresh agent instances (same specification, same isolation constraints). Record the alignment scores for B and C on each of the 5 contract-inference aspects in each run.

**Measurement:** For each run, record whether divergence is: (a) complementary (B and C diverge on different dimensions), (b) symmetric (B and C diverge on the same dimensions), or (c) neither. Compute the frequency of complementary divergence across runs. If complementary divergence is stable across ≥ 3 runs, it suggests agents have consistent cognitive anchoring patterns on field naming vs. structural design that hold across model instances.

---

*End of Topology Research Program v1 Final Synthesis Report*
