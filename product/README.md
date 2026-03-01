# Bookmark Manager API

A minimal REST API for managing bookmarks, built with FastAPI and in-memory storage.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --port 8000
```

## Endpoints

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Create a bookmark

```bash
curl -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Example", "tags": ["python", "web"]}'
# {"id":"<uuid>","url":"https://example.com","title":"Example","tags":["python","web"]}
```

### List all bookmarks

```bash
curl http://localhost:8000/bookmarks
# [{"id":"...","url":"...","title":"...","tags":[...]}]
```

### List bookmarks filtered by tag

```bash
curl "http://localhost:8000/bookmarks?tag=python"
# returns only bookmarks whose tags list contains "python"
```

### Get a bookmark by ID

```bash
curl http://localhost:8000/bookmarks/<id>
# {"id":"...","url":"...","title":"...","tags":[...]}
# 404 if not found
```

### Delete a bookmark

```bash
curl -X DELETE http://localhost:8000/bookmarks/<id>
# returns the deleted bookmark
# 404 if not found
```
