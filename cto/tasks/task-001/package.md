# Task 001: Bootstrap product context and implement REST API

## System Prompt
You are a Node.js backend engineer working on a greenfield project. Your job is to set up the product context file and implement a simple REST API using Express with in-memory storage. You write clean, minimal code — no unnecessary complexity, no over-engineering.

## Assignment

### Part 1: Fill in product/CLAUDE.md
Update `product/CLAUDE.md` with accurate project details reflecting what you are about to build:
- What it is: a simple REST API built with Node.js + Express
- Tech stack: Node.js, Express, in-memory storage (no database)
- How to run: `npm install` then `node index.js` (starts on port 3000)
- Project structure: reflect the files you create
- Code conventions: keep it simple — CommonJS, single `index.js` entry point

### Part 2: Implement the REST API in product/

Create `product/index.js` with these endpoints:

| Method | Path | Behavior |
|--------|------|----------|
| GET | /health | Returns `{ "status": "ok" }` |
| GET | /items | Returns array of all items |
| POST | /items | Creates item with `{ name: string }`. Returns 400 if `name` is missing/empty. Returns created item with `id` and `name`. |
| GET | /items/:id | Returns item by id. Returns 404 if not found. |
| DELETE | /items/:id | Deletes item by id. Returns 404 if not found. Returns deleted item or confirmation. |

Create `product/package.json` with `express` as a dependency.

### Acceptance Criteria
- `node index.js` starts the server on port 3000 with no errors
- All 5 endpoints respond correctly to valid requests
- POST /items returns 400 when `name` is missing or empty string
- GET /items/:id and DELETE /items/:id return 404 when id doesn't exist
- Code is clean and readable — no unnecessary files, no TypeScript, no test frameworks
- `product/CLAUDE.md` is filled in accurately

## Relevant Files
- `product/CLAUDE.md` — fill this in first
- `product/index.js` — create this (main entry point)
- `product/package.json` — create this
