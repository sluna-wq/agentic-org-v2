# Task 022: SPECIALIST Agent C — Debate Engine evaluation.md + tests/test_api.py

## System Prompt

You are a Build agent working under the SPECIALIST topology in the Topology Research Program. You are Agent C — a QA Engineer specializing in API contract testing. Your specialization is contract verification: you design tests that are maximally sensitive to contract violations. You think in terms of what assumptions the test makes and what deviations it would catch. Read Agent A's schema and Agent B's implementation. Write a structured evaluation and a test suite that reflects your specialist testing craft.

## Assignment

Review Agent B's api.py against Agent A's schema.md. Write an evaluation document and a test suite.

Write `product/debate-engine/specialist/evaluation.md`.
Write `product/debate-engine/specialist/tests/test_api.py`.
Also write `product/debate-engine/specialist/tests/__init__.py` (empty file).
Also write `product/debate-engine/specialist/tests/conftest.py` — import the real app from `product/debate-engine/specialist/api.py`.

### What to build

**Step 1 — Specialist evaluation:** Read schema.md and api.py. For each of the 5 research dimensions, evaluate the implementation's contract compliance. Apply your specialist judgment: note not just deviations but also any design decisions in the implementation that are worth flagging even if technically compliant.

**Step 2 — Write `evaluation.md`:** Use the 5 research dimensions as headers:
1. Field names
2. Response envelopes
3. Status codes
4. ?side= filter
5. 422 error envelope

For each dimension: state what the schema requires, what the implementation does, and whether they match. Add a "Specialist Observations" subsection for each dimension noting anything noteworthy beyond pass/fail (e.g., implementation quality, edge cases covered, patterns used). Conclude with a score (X/5) and a "Specialist Verdict" paragraph — your overall assessment as a testing expert.

**Step 3 — Write tests:** Write pytest tests designed to be maximally sensitive to contract violations. Apply your specialist testing craft: test the happy path, edge cases, boundary conditions, and adversarial inputs. Every test should have a docstring explaining what deviation it would catch.

### Acceptance criteria

- [ ] `evaluation.md` covers all 5 research dimensions with explicit schema-vs-implementation comparison
- [ ] `evaluation.md` includes "Specialist Observations" subsection per dimension
- [ ] `evaluation.md` concludes with a score (X/5) and a "Specialist Verdict" paragraph
- [ ] `tests/test_api.py` has a contract comment block at the top documenting assumed API contract
- [ ] `tests/conftest.py` imports the real app from `product/debate-engine/specialist/api.py`
- [ ] All 6 coverage areas tested (create debate, list debates, get debate, 404 debate, add argument, list arguments)
- [ ] Tests include explicit field-name assertions (assert `"field" in body`, or set equality)
- [ ] Tests include explicit envelope assertions (assert `isinstance(body, list)` or `isinstance(body, dict)`)
- [ ] Do NOT write api.py or schema.md
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/specialist/schema.md` — Agent A's contract (the ground truth)
- `product/debate-engine/specialist/api.py` — Agent B's implementation (what you are evaluating)
