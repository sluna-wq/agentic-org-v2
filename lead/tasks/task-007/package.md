# Task 007: Fix orchestrator env vars + deploy dashboard to GitHub Pages

## System Prompt

You are a Build agent making infrastructure changes to this agentic repo. You will fix a variable name mismatch in the GitHub Actions workflow and add a GitHub Pages deployment job, plus update the dashboard HTML defaults so it works out of the box.

**Expanded write access for this task only (explicitly authorized by Lead):**
- `.github/workflows/orchestrator.yml`
- `product/dashboard/index.html`
- `product/dashboard/README.md`
- Your own `lead/tasks/task-007/status.md`

## Assignment

### Problem 1 — env var name mismatch

`.github/workflows/orchestrator.yml` passes `CTO_MAX_TURNS` and `TASK_MAX_TURNS` as env vars, but `orchestrator.sh` reads `LEAD_MAX_TURNS` and `BUILD_MAX_TURNS`. The workflow vars never reach the script.

**Fix:** In `.github/workflows/orchestrator.yml`:
- Rename input `cto_max_turns` → `lead_max_turns`, input `task_max_turns` → `build_max_turns`
- Rename env vars `CTO_MAX_TURNS` → `LEAD_MAX_TURNS`, `TASK_MAX_TURNS` → `BUILD_MAX_TURNS`
- Update all references (inputs, env block, any `${{ inputs.xxx }}` interpolations)

### Problem 2 — no native dashboard access

Deploy `product/dashboard/index.html` to GitHub Pages so it's accessible at `https://sluna-wq.github.io/agentic-org-v2/`.

**Fix:** Add a second job `deploy-pages` to `.github/workflows/orchestrator.yml`:
- Runs after the `run` job succeeds (`needs: run`)
- Add to the top-level `permissions:` block: `pages: write` and `id-token: write`
- Steps:
  1. `actions/checkout@v4`
  2. Copy `product/dashboard/index.html` to a staging dir (e.g., `_site/index.html`)
  3. `actions/upload-pages-artifact@v3` pointing at the staging dir
  4. `actions/deploy-pages@v4`
- Use `environment: github-pages` on the job

### Problem 3 — dashboard defaults

In `product/dashboard/index.html`, set the default config values so the dashboard works immediately when loaded from Pages without configuration:
- Find where the JS loads localStorage config or sets default values for `owner` and `repo`
- Set `owner = 'sluna-wq'` and `repo = 'agentic-org-v2'` as the defaults (only used if localStorage has no saved config)

### Problem 4 — README update

In `product/dashboard/README.md`, add the Pages URL prominently at top:
```
Live: https://sluna-wq.github.io/agentic-org-v2/
```

### Acceptance criteria
- [ ] `orchestrator.yml` env var names match `orchestrator.sh` exactly (`LEAD_MAX_TURNS`, `BUILD_MAX_TURNS`)
- [ ] `deploy-pages` job exists in the workflow with correct permissions, `needs: run`, and all 4 steps
- [ ] Dashboard HTML has `owner = 'sluna-wq'` and `repo = 'agentic-org-v2'` as hardcoded defaults
- [ ] `product/dashboard/README.md` has the Pages URL at top

## Relevant Files

- `.github/workflows/orchestrator.yml` — fix env var names, add deploy-pages job
- `product/dashboard/index.html` — set default owner/repo in JS config section
- `product/dashboard/README.md` — add Pages URL
