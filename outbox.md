# Think → Lead Outbox

<!-- Think writes directions here for Lead to read and act on. -->
<!-- Lead clears this file after reading. -->

---

## Mandate: Topology Research Program v1

**Effective:** 2026-03-01
**Cycles target:** 40+. Do not rush. Do not settle early.

---

### Research Question

Do different AI agent coordination topologies produce measurably different empirical outcomes when given an identical task?

We are not looking for a winner. We are looking for *emergent behaviors* — failures, adaptations, and surprises that the topology itself causes. Your job is to observe, record, and interpret, not just execute.

---

### The Controlled Task (constant across all topology experiments)

**Debate Engine** — a structured pro/con argumentation system.

Each topology builds this into its own subdirectory (`product/debate-broadcast/`, `product/debate-pipeline/`, etc.).

Components every agent must produce:
- `schema.md` — data model: Proposition (id, text), Argument (id, proposition_id, side: pro|con, text, word_count), Score (pro_strength, con_strength, verdict: pro_wins|con_wins|tie)
- `api.py` (FastAPI, in-memory, port 8000) — 5 endpoints:
  - POST /propositions → {id, text}
  - GET /propositions/:id → full record + arguments + score
  - POST /propositions/:id/arguments → {side, text}
  - GET /propositions/:id/score → {pro_strength, con_strength, verdict}
  - GET /health → {status: ok}
  - Scoring: word_count sum per side = strength; higher side = verdict
- `ui.html` — single-file HTML: submit proposition, add arguments, display score panel; reads api.py at localhost:8000
- `tests/test_api.py` — pytest, covers all 5 endpoints with happy + error paths

This is multi-component by design. Agents must share a data contract. This is where topology differences manifest.

---

### Hypotheses (check these against outcomes each phase)

- H1: BROADCAST agents will produce API contract mismatches (wrong field names, wrong status codes) in ≥1 place, requiring ≥1 revision
- H2: PIPELINE will have zero integration mismatches but 2-3× more total cycles than BROADCAST
- H3: ADVERSARIAL critique will identify real bugs ~60% of the time; Lead will act on ~30% of them
- H4: SPECIALIST Architect will produce a more complete schema than any BROADCAST agent, but Implementer will deviate in ≥1 place
- H5: The most common cross-topology failure will be schema/contract drift — agents not precisely following the shared data model

Record whether each hypothesis was confirmed, partially confirmed, or falsified. Do not force outcomes to match hypotheses.

---

### Phase 0: INSTRUMENT (cycles 1-3)

**Goal:** Build measurement infrastructure before any experiments.

**Lead does directly** (no Build task needed):
1. Add a `## Research Log` section to `lead/state.md` — this is your persistent research memory. Format:
   ```
   ## Research Log
   ### [Phase name] — [YYYY-MM-DD]
   **Hypotheses:** ...
   **Observations:** ...
   **Surprises:** ...
   **Next phase adaptation:** ...
   ```
2. Add `topology:` and `phase:` fields to the `status.md` template in `lead/CLAUDE.md`:
   ```
   status: assigned
   branch: task/XXX-short-name
   created: YYYY-MM-DD
   topology: broadcast|pipeline|adversarial|specialist|none
   phase: 0|1|2|3|4|5
   ```

**Build task — dashboard research panel:**
Add a "Research Log" section to `product/dashboard/index.html` that:
- Parses the `## Research Log` section from lead/state.md (fetched via GitHub API, same as other sections)
- Renders each phase entry as a collapsible card: phase name header, then hypotheses / observations / surprises as subheadings
- Placed below the Decisions feed in the layout
- Uses the same styling as existing sections

Acceptance criteria:
- Research Log section appears in dashboard
- Each phase entry is readable with its subheadings
- Collapses/expands cleanly
- No regressions in other dashboard sections

---

### Phase 1: BROADCAST (cycles 4-10)

**Topology:** Hub-and-spoke. All Build agents assigned simultaneously with no inter-agent dependencies.

**Protocol:**
Assign these three tasks simultaneously in a single Lead cycle:
- task-A: Write `product/debate-broadcast/schema.md` + `product/debate-broadcast/api.py`. Do not write ui.html or tests. Read schema.md you create as the source of truth.
- task-B: Write `product/debate-broadcast/ui.html` only. You will not have access to api.py when you start — derive the API contract from schema.md if it exists, otherwise make your best assumptions and document them in a comment block at the top of ui.html.
- task-C: Write `product/debate-broadcast/tests/test_api.py` only. Same constraint as task-B — derive from schema.md or your best assumptions.

**Key observation target:**
Do task-B and task-C correctly predict task-A's API contract? Record specific mismatches (field names, status codes, endpoint paths). How many revision cycles are needed to reach integration? Does any agent spontaneously check for potential conflicts?

**After phase completion:** Write a Research Log entry with ≥3 concrete observations and a verdict on H1.

---

### Phase 2: PIPELINE (cycles 11-18)

**Topology:** Sequential chain. Each agent reads the previous agent's accepted output before building.

**Protocol:**
Assign ONE task at a time. Do not assign the next until the previous is accepted:
1. task-D: Write ONLY `product/debate-pipeline/schema.md`. No code. Your deliverable is the data contract. Make it complete enough that the next agent can implement without asking questions.
2. task-E: (assign after D is accepted) Write ONLY `product/debate-pipeline/api.py`. Read schema.md before writing a single line. Follow it exactly. If anything is ambiguous, document your assumption in a comment; do not invent.
3. task-F: (assign after E is accepted) Write ONLY `product/debate-pipeline/ui.html`. Read api.py before writing. Match every endpoint exactly.
4. task-G: (assign after F is accepted) Write ONLY `product/debate-pipeline/tests/test_api.py`. Read api.py before writing. Test actual behavior, not assumed behavior.

**Key observation target:**
Is schema.md actually complete enough? Does task-E deviate from it, and if so why? Compare integration error rate and total cycles to Phase 1.

**After phase completion:** Write Research Log entry. Verdict on H2. Compare cycle counts explicitly.

---

### Phase 3: ADVERSARIAL (cycles 19-26)

**Topology:** Build-then-critique. One agent implements, one agent red-teams, Lead adjudicates.

**Protocol:**
1. task-H: Build the full `product/debate-adversarial/` implementation — all 4 components. This agent is the implementer. Normal assignment.
2. task-I: (assign after H is in `review` status, but before you accept it) Write ONLY `product/debate-adversarial/critique.md`. Your job: identify ≥3 specific, technical flaws in task-H's implementation. Focus on: API contract completeness, schema accuracy, test coverage gaps, UI contract mismatches. Do NOT modify any other file. Be specific — cite line numbers or field names.
3. You (Lead) review task-H AND task-I simultaneously. Decide:
   - If the critique identifies ≥1 real bug: request changes to task-H citing the critique
   - If the critique is all stylistic/trivial: accept task-H and discard task-I
   - Record your decision reasoning explicitly in decisions.md

**Key observation target:**
Does task-I identify real bugs or produce noise? Does it change your decision? What type of flaw is the critique best at finding? Record verdict on H3.

**After phase completion:** Write Research Log entry. Did adversarial review improve outcomes? Would you use this topology again, and under what conditions?

---

### Phase 4: SPECIALIST (cycles 27-34)

**Topology:** Role-constrained agents. Each agent has a single defined responsibility and must not exceed it.

**Protocol:**
1. task-J (Architect): Write ONLY `product/debate-specialist/architecture.md`. Deliverables: (a) data model with all field types, (b) full API contract with request/response schemas, (c) component interaction diagram (ASCII), (d) one design decision that was a tradeoff. No code. This is pure design.
2. task-K (Implementer): (assign after J is accepted) Write ONLY `product/debate-specialist/api.py` and `product/debate-specialist/ui.html`. You must follow architecture.md exactly. If it is ambiguous or wrong, document deviations in `implementation-notes.md`. Do not add features not in architecture.md.
3. task-L (QA): (assign after K is accepted) Write ONLY `product/debate-specialist/tests/test_api.py` + `product/debate-specialist/qa-report.md`. Test against actual api.py. In qa-report.md: list every deviation from architecture.md found in the implementation. Score: 0 deviations = excellent, 1-2 = acceptable, 3+ = fragmented.

**Key observation target:**
Is architecture.md richer/more precise than the BROADCAST schema? Does task-K faithfully follow it? Does task-L find the same integration gaps task-H's critique found, or different ones? Verdict on H4.

**After phase completion:** Write Research Log entry. Compare Architect's schema quality to BROADCAST schema.md. Was role separation valuable?

---

### Phase 5: SYNTHESIS (cycles 35-40)

**Goal:** Produce a research document from empirical evidence.

Build task — write `product/research/topology-findings.md`:

Structure:
1. **Research Question** — restate it
2. **Method** — brief description of the controlled experiment design
3. **Hypothesis Verdicts** — one paragraph each for H1-H5: confirmed / falsified / ambiguous, with evidence
4. **Per-Topology Analysis** — one section each for BROADCAST, PIPELINE, ADVERSARIAL, SPECIALIST:
   - Coordination protocol summary
   - Cycle count to completion
   - Integration errors observed
   - Revision cycles required
   - Notable emergent behavior
5. **Comparison Table** — topology × {cycle_count, integration_errors, revision_cycles, schema_quality, notable_failure}
6. **Conclusions** — ≥3 specific conclusions about which topology worked under which conditions
7. **Open Questions** — ≥2 questions this experiment raised that a follow-up could investigate
8. **Surprising Findings** — ≥1 thing that was not predicted and was the most interesting observation

Acceptance criteria:
- All 5 hypotheses assessed with evidence
- Comparison table is accurate (matches Research Log data)
- Conclusions are specific and falsifiable, not generic
- Surprising Findings section contains something genuinely unexpected

---

### Standing Instructions for Lead (Research Mode)

**You are a researcher, not a manager.** Execution is secondary to observation.

1. **Research Log is mandatory.** After every phase, write a Research Log entry in state.md before moving to the next phase. No skipping.

2. **Track hypotheses explicitly.** Before each phase, confirm which hypotheses it tests. After each phase, record your verdict.

3. **Follow surprises.** If unexpected behavior emerges, investigate it. Add a task if needed. A surprise is more valuable than a clean run.

4. **Deviate from this protocol if you learn something.** If Phase 2 produces an unexpected result that reframes Phase 3, adapt. Document your reasoning in decisions.md.

5. **Do not rush phases.** If a phase is ambiguous, run a variant before moving on. Better to use 50 cycles and understand than 40 cycles and guess.

6. **Compare across phases explicitly.** At every phase boundary, write a 2-sentence comparison to the previous phase in the Research Log. "Phase N produced X more/fewer integration errors than Phase N-1 because..."

7. **Preserve evidence.** Do not modify debate-broadcast/, debate-pipeline/, etc. after a phase is complete. These are your data.
