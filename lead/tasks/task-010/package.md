# Task 010: Dashboard Research Panel

## System Prompt

You are a Build agent. You implement exactly what is assigned — no more, no less. You write production-quality code and commit your work. You do not push. When done, you set your task status to `review`.

## Assignment

Add a **Research Log** section to `product/dashboard/index.html`.

The dashboard already fetches `lead/state.md` from the GitHub API and parses other sections from it (mandate, backlog, decisions). Extend it to also parse and render the `## Research Log` section.

### What to build

1. **Parse** the `## Research Log` section from the already-fetched `lead/state.md` content. The section contains sub-entries formatted as:
   ```
   ### [Phase name] — [YYYY-MM-DD]
   **Hypotheses:** ...
   **Observations:** ...
   **Surprises:** ...
   **Next phase adaptation:** ...
   ```

2. **Render** each phase entry as a collapsible card:
   - The card header shows the phase name and date (e.g., "Phase 0: INSTRUMENT — 2026-03-01")
   - Clicking the header expands/collapses the card body
   - The card body renders the four subheadings (**Hypotheses**, **Observations**, **Surprises**, **Next phase adaptation**) with their content
   - Cards start collapsed by default

3. **Place** the Research Log section below the Decisions feed in the existing layout.

4. **Style** using the same CSS patterns already present in the dashboard (same card/section styles, same font, same color palette). Do not introduce new stylesheets or frameworks.

### Acceptance criteria

- [ ] Research Log section header appears in the dashboard
- [ ] Each `### Phase X` entry renders as a collapsible card with correct header text
- [ ] Subheadings (Hypotheses, Observations, Surprises, Next phase adaptation) are visually distinct within each card
- [ ] Cards collapse/expand cleanly on click
- [ ] If the `## Research Log` section is absent from state.md, the section renders gracefully (e.g., "No research log entries yet")
- [ ] No regressions in other dashboard sections (mandate, task board, decisions feed, cycle timeline still work)

## Relevant Files

- `product/dashboard/index.html` — the single file to modify; read it fully before touching anything
- `lead/state.md` — shows the `## Research Log` format your parser must handle
