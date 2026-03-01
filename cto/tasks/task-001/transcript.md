All done. Here's a summary of what was delivered:

**Files created/updated:**
- `product/CLAUDE.md` — filled in with project description, tech stack, run instructions, conventions, and structure
- `product/package.json` — `express ^4.18.2` as the only dependency
- `product/index.js` — Express app with all 5 endpoints:
  - `GET /health` → `{ status: "ok" }`
  - `GET /items` → array of all items
  - `POST /items` → creates item; 400 if `name` missing/empty; 201 with `{ id, name }` on success
  - `GET /items/:id` → item by id; 404 if not found
  - `DELETE /items/:id` → removes and returns item; 404 if not found

**Status:** Task committed to branch `task/001-rest-api`, status updated to `review`.
