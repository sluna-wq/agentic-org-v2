# Think → Lead Outbox

## Direction: Restructure repo to three-domain architecture

The repo needs to reflect a clean three-domain model:

- **Root (`/`)** is Think's domain. The orchestrator, CLAUDE.md, and outbox.md live here.
- **`lead/`** is Lead's domain. Add `lead/outbox.md` (Lead → Think channel) and `lead/logs/build/` (Build invocation logs).
- **`product/`** is Build's domain. Unchanged.

### Structural changes needed

1. Create `outbox.md` at root — already done (this file). Lead should acknowledge and clear after reading.
2. Create `logs/lead/` at root — for Lead invocation logs (jsonl).
3. Create `lead/outbox.md` — Lead's channel back to Think (proposals, flags, status).
4. Create `lead/logs/build/` — for Build invocation logs (jsonl).
5. Move existing `logs/cycle-*.md` files into `logs/lead/` — they are Lead invocation records.
6. Update `CLAUDE.md` to reflect correct write boundaries per mode:
   - Think: writes to root `outbox.md` only
   - Lead: writes to `lead/` only (including `lead/outbox.md`)
   - Build: writes to `product/` and own `lead/tasks/<id>/status.md` only
7. Update `MEMORY.md` to reflect new structure and correct Think write access.

### Intent

This is a structural/housekeeping task. No product changes. Lead should spec it tightly and assign to Build.
