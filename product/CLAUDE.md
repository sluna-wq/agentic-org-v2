# Product

A simple REST API for managing a list of items. Built with Node.js and Express, using in-memory storage. No database required.

---

## What This Is

A minimal CRUD REST API that lets clients create, read, and delete named items. Items are stored in memory — data resets on restart. Intended as a clean, dependency-light backend service.

---

## Tech Stack

- **Runtime:** Node.js (CommonJS)
- **Framework:** Express
- **Storage:** In-memory array (no database)

---

## Running the Project

```bash
# Install dependencies
npm install

# Start server (runs on port 3000)
node index.js
```

---

## Code Conventions

- CommonJS (`require`/`module.exports`) — no ESM
- Single entry point: `index.js`
- No TypeScript, no test frameworks, no build step
- Keep logic inline — no separate route files for a project this size
- IDs are auto-incrementing integers

---

## Project Structure

```
product/
├── index.js       — Express app and all route handlers
├── package.json   — Dependencies (express only)
└── CLAUDE.md      — This file
```

---

## Notes for Task Agents

- Always read this file before writing any code.
- Follow the conventions listed here exactly.
- If you discover something missing from this file that future agents should know, note it in your task transcript — the CTO may update this file.
- Do not modify this file directly unless your task assignment explicitly says to.
