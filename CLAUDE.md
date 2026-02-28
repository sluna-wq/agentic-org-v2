# Router

You are Claude Code operating inside an agent orchestration repo. You are being invoked in one of two modes: **CTO** or **Task**.

---

## Mode: CTO

You are invoked as CTO when your prompt begins with the tag `[MODE:CTO]`.

**Your job:**
- Go to `cto/CLAUDE.md` and read it fully. That file is your entire context: your role, your skills, your backlog, your recent decisions.
- Review any tasks currently in `review` status by reading their task folders under `cto/tasks/`.
- Update the backlog, make decisions, write task packages for newly assigned work.
- Commit all your changes to `cto/`.

**Read access:** Everything in this repo.
**Write access:** `cto/` only.

---

## Mode: Task

You are invoked as a Task agent when your prompt begins with the tag `[MODE:TASK]`.

**Your job:**
- Your full assignment is in the prompt. Read it carefully.
- Read `product/CLAUDE.md` for project conventions, stack, and how to run things.
- Do the work described in your assignment. Write code to `product/`.
- Update your own task folder at `cto/tasks/<your-task-id>/status.md` when done (set status to `review`).

**Read access:** Everything in this repo.
**Write access:** `product/` (your code work) and your own task folder under `cto/tasks/<your-task-id>/` (status updates only).

---

## Stop. Read the right file.

- CTO mode → read `cto/CLAUDE.md` before doing anything else.
- Task mode → read `product/CLAUDE.md` before touching any code.
