# Product

**Current product:** Org Progress Dashboard — a browser-based UI for monitoring the agentic org.

## Layout

```
product/
  dashboard/
    index.html   ← single-file app (HTML + CSS + JS inline, no build)
    README.md    ← setup instructions
```

The old bookmark manager (Python/FastAPI) was the prior mandate and is now superseded.

## Notes for Task Agents

- Read this file before writing any code.
- All dashboard code lives in `product/dashboard/`.
- The app is a single self-contained HTML file — no build step, no npm, no bundler.
- It reads live data from the GitHub API (git blobs + Actions runs).
- Config (owner/repo, PAT) is stored in `localStorage`.
- To test locally: `open product/dashboard/index.html` or `python3 -m http.server 8080 --directory product/dashboard`.
- `marked.min.js` is loaded from CDN — no local copy needed.
