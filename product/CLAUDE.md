# Product

Bookmark manager REST API — Python + FastAPI, in-memory storage.

## Project layout

```
product/
  main.py           # FastAPI app — all 5 endpoints
  requirements.txt  # Pinned deps: fastapi, uvicorn, pydantic
  README.md         # curl examples for every endpoint
  CLAUDE.md         # This file
```

## How to run

```bash
pip install -r requirements.txt
uvicorn main:app --port 8000
```

## Notes for Task Agents

- Read this file before writing any code.
- All code goes in `product/`.
- Server starts with: `uvicorn main:app --port 8000`
- Storage is in-memory (`_bookmarks` dict in `main.py`) — no database.
- URL validation uses Pydantic `AnyHttpUrl`; invalid URLs return 422.
- Update this file when you change the project layout.
