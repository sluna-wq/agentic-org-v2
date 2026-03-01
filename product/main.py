from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from typing import List, Optional
import uuid

app = FastAPI()

# In-memory store: id -> bookmark dict
_bookmarks: dict[str, dict] = {}


class BookmarkIn(BaseModel):
    url: AnyHttpUrl
    title: str
    tags: List[str] = []


class BookmarkOut(BaseModel):
    id: str
    url: str
    title: str
    tags: List[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/bookmarks", response_model=BookmarkOut, status_code=201)
def create_bookmark(bookmark: BookmarkIn):
    bm_id = str(uuid.uuid4())
    bm = {
        "id": bm_id,
        "url": str(bookmark.url),
        "title": bookmark.title,
        "tags": bookmark.tags,
    }
    _bookmarks[bm_id] = bm
    return bm


@app.get("/bookmarks", response_model=List[BookmarkOut])
def list_bookmarks(tag: Optional[str] = None):
    result = list(_bookmarks.values())
    if tag is not None:
        result = [b for b in result if tag in b["tags"]]
    return result


@app.get("/bookmarks/{bm_id}", response_model=BookmarkOut)
def get_bookmark(bm_id: str):
    bm = _bookmarks.get(bm_id)
    if bm is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bm


@app.delete("/bookmarks/{bm_id}", response_model=BookmarkOut)
def delete_bookmark(bm_id: str):
    bm = _bookmarks.pop(bm_id, None)
    if bm is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bm
