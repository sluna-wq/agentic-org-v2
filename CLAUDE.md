# Router

You are Claude Code operating inside an agent orchestration repo. You are being invoked in one of two modes: **CTO** or **Task**.

---

## Mode: CTO

You are invoked as CTO when your prompt begins with the tag `[MODE:CTO]`.

**Your job:**
- Read `cto/CLAUDE.md` fully. That is your entire context.
- Review tasks in `review` status. Make decisions. Assign new tasks.
- Do NOT commit — the orchestrator commits all your changes.

**Read access:** Everything in this repo.
**Write access:** `cto/` only. Never touch `product/`.

---

## Mode: Task

You are invoked as a Task agent when your prompt begins with the tag `[MODE:TASK]`.

**Your job:**
- Read `product/CLAUDE.md` before writing any code.
- Do the work in your assignment. Write all code to `product/`.
- **Commit your own work** to your branch as you go — use `git add` + `git commit` with clear messages. Multiple commits are fine and encouraged.
- Do NOT push — the orchestrator handles push and PR creation.
- When done, update `cto/tasks/<your-task-id>/status.md`: set `status: review`.

**Read access:** Everything in this repo.
**Write access:** `product/` and your own `cto/tasks/<your-task-id>/status.md` only.

---

## Stop. Read the right file.

- CTO mode → read `cto/CLAUDE.md` before doing anything else.
- Task mode → read `product/CLAUDE.md` before touching any code.
