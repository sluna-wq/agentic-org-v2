# Task 023: SYNTHESIS — Topology Research Program v1 Final Report

## System Prompt

You are a Build agent completing Phase 5 (Synthesis) of the Topology Research Program. Your job is to write the final cross-topology comparison report. You are not implementing any API code — you are a research analyst reading the accumulated evidence from Phases 1–4 and synthesising findings into a coherent, evidence-based document.

## Assignment

Write the final synthesis report for the Topology Research Program v1.

Write `product/debate-engine/synthesis/report.md`.

### What to build

Read the following files before writing anything:

**Schemas (what each Agent A produced):**
- `product/debate-engine/broadcast/schema.md`
- `product/debate-engine/pipeline/schema.md`
- `product/debate-engine/adversarial/schema.md`
- `product/debate-engine/specialist/schema.md`

**Implementations (what each Agent B produced):**
- `product/debate-engine/broadcast/api.py` (if it exists)
- `product/debate-engine/pipeline/api.py`
- `product/debate-engine/adversarial/api.py`
- `product/debate-engine/specialist/api.py`

**Evaluations (what each Agent C produced):**
- `product/debate-engine/pipeline/critique.md` (if it exists — check)
- `product/debate-engine/adversarial/critique.md`
- `product/debate-engine/specialist/evaluation.md`

**Test suites (what each Agent C produced):**
- `product/debate-engine/broadcast/tests/test_api.py` (if it exists)
- `product/debate-engine/pipeline/tests/test_api.py`
- `product/debate-engine/adversarial/tests/test_api.py`
- `product/debate-engine/specialist/tests/test_api.py`

### Report structure

Write `report.md` with the following sections:

#### 1. Program Overview
Brief description of the research question, controlled task (Debate Engine), and the 4 topologies tested (BROADCAST, PIPELINE, ADVERSARIAL, SPECIALIST). One paragraph each.

#### 2. Hypotheses
List H1–H4 as stated in the research program. For each:
- What was predicted
- What was observed
- Verdict: SUPPORTED / PARTIALLY SUPPORTED / REFUTED / INCONCLUSIVE

#### 3. Cross-Topology Comparison
A structured comparison across the 5 research dimensions, for each topology's Agent B (implementation) evaluated against Agent A's schema:

| Topology | Field Names | Response Envelopes | Status Codes | ?side= Filter | 422 Envelope | Total |
|---|---|---|---|---|---|---|
| BROADCAST | | | | | | /5 |
| PIPELINE | | | | | | /5 |
| ADVERSARIAL | | | | | | /5 |
| SPECIALIST | | | | | | /5 |

For each cell: PASS or FAIL (or N/A if not measured). Populate from evaluation documents.

#### 4. Emergent Findings
Observations that were not in the original hypotheses but emerged from the data. Examples:
- Schema quality differences between topologies (constraint count, explicitness)
- Test count differences (BROADCAST vs PIPELINE vs ADVERSARIAL vs SPECIALIST)
- New fields or design decisions that emerged only in certain topologies (e.g., argument_count, total field in envelopes, ordering specification)
- Framing effects: did specialist/adversarial identity change output quality independent of structural topology?

#### 5. Methodology Notes
Document any methodological limitations or confounds observed:
- Single-author GitHub review constraint
- Any conflicting signals in task assignments (e.g., SPECIALIST 422 assignment conflict)
- What was held constant across topologies, what varied

#### 6. Conclusions
3–5 concrete, evidence-backed conclusions. Each should be specific enough to guide future research or practical topology choice. Avoid vague generalities.

#### 7. Suggested Future Research
3–5 specific follow-on experiments that this program's data suggests are worth running. Each should identify: the question, the proposed design, and the specific measurement.

### Acceptance criteria

- [ ] All 4 topology schemas read and compared (field names, constraints, new fields)
- [ ] Cross-topology comparison table populated for all 5 dimensions
- [ ] H1–H4 explicitly stated and verdict given for each
- [ ] Emergent findings section identifies at least 3 observations not in original hypotheses
- [ ] Test counts compared across all topologies (BROADCAST, PIPELINE 29, ADVERSARIAL 61, SPECIALIST 71)
- [ ] Methodology notes address the single-author constraint and the SPECIALIST 422 confound
- [ ] Conclusions are specific and evidence-backed (no vague generalities)
- [ ] Suggested future research includes at least 3 specific experiments
- [ ] Do NOT write any api.py, schema.md, or test files
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `lead/state.md` — contains Research Log with per-phase observations and hypothesis tracking
- All schema.md, api.py, critique.md/evaluation.md, and test_api.py files listed above
