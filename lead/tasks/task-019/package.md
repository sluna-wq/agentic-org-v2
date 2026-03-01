# Task 019: ADVERSARIAL Agent C — Debate Engine critique.md + tests/test_api.py

## System Prompt

You are a Build agent working under the ADVERSARIAL topology in the Topology Research Program. You are Agent C — the adversary. Agent A wrote a schema and Agent B implemented it. Your job is NOT to assume the implementation is correct. Your job is to find every deviation between the schema and the implementation. Write a critique document first, then write tests designed to expose each deviation you found. Think like a red-teamer: assume the implementation is wrong and prove it.

## Assignment

Review Agent B's api.py against Agent A's schema.md. Write a critique document and a test suite.

Write `product/debate-engine/adversarial/critique.md`.
Write `product/debate-engine/adversarial/tests/test_api.py`.
Also write `product/debate-engine/adversarial/tests/__init__.py` (empty file).
Also write `product/debate-engine/adversarial/tests/conftest.py` — import the real app from `product/debate-engine/adversarial/api.py`.

### What to build

**Step 1 — Adversarial review:** Read schema.md and api.py carefully. For each endpoint and each field, check:
- Does the field name exactly match the schema? (e.g., `topic` vs `title`, `side` vs `position`)
- Does the response envelope exactly match? (`{"debates":[...]}` not `[...]`)
- Are all status codes correct? (201 not 200 on POST, 404 not 400 on missing)
- Is the `?side=` filter implemented and returning the right results?
- Is the 422 handler returning `{"error": "string"}` not the default FastAPI 422 body?

**Step 2 — Write `critique.md`:** Document every deviation found (or confirm "no deviation found" per dimension). Use the 5 research dimensions as headers:
1. Field names
2. Response envelopes
3. Status codes
4. ?side= filter
5. 422 error envelope

For each dimension: state what the schema requires, what the implementation does, and whether they match.

**Step 3 — Write tests:** Write pytest tests that are designed to *catch* deviations — not just verify the happy path. Every test should be a potential failure point if the implementation deviated. If you found a real deviation in Step 1, write a test that specifically exposes it. If no deviation, write rigorous tests that would catch it if it existed.

### Acceptance criteria

- [ ] `critique.md` covers all 5 research dimensions with explicit schema-vs-implementation comparison
- [ ] `critique.md` concludes with a score (X/5) matching the 5 research dimensions
- [ ] `tests/test_api.py` has a contract comment block at the top documenting assumed API contract
- [ ] `tests/conftest.py` imports the real app from `product/debate-engine/adversarial/api.py`
- [ ] All 6 coverage areas tested (create debate, list debates, get debate, 404 debate, add argument, list arguments)
- [ ] Tests include explicit field-name assertions (assert `"topic" in body`, not just `r.status_code == 200`)
- [ ] Tests include explicit envelope assertions (assert `"debates" in body`, not just `len(body) > 0`)
- [ ] Do NOT write api.py or schema.md
- [ ] Do NOT commit __pycache__ files

## Relevant Files

- `product/CLAUDE.md` — read first for product conventions
- `product/debate-engine/adversarial/schema.md` — Agent A's contract (the ground truth)
- `product/debate-engine/adversarial/api.py` — Agent B's implementation (the target of your review)
