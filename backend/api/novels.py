# backend/api/novels.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.novel import NovelMeta, CreateNovelRequest
from services.file_service import (
    NOVELS_DIR, get_novel_dir, init_novel_structure,
    read_json, write_json, generate_id, now_iso, novel_exists,
)
import os

router = APIRouter()


@router.get("/novels", response_model=list[NovelMeta])
def list_novels():
    """List all novel projects."""
    if not os.path.isdir(NOVELS_DIR):
        return []
    novels = []
    for entry in os.listdir(NOVELS_DIR):
        meta_path = os.path.join(NOVELS_DIR, entry, "metadata.json")
        if os.path.isfile(meta_path):
            meta = read_json(meta_path)
            if meta:
                novels.append(NovelMeta(**meta))
    novels.sort(key=lambda n: n.updatedAt, reverse=True)
    return novels


@router.post("/novels", response_model=NovelMeta)
def create_novel(req: CreateNovelRequest):
    """Create a new novel project."""
    novel_id = generate_id()
    init_novel_structure(novel_id)

    meta = NovelMeta(
        id=novel_id,
        title=req.title,
        author=req.author,
        topic=req.topic,
        genre=req.genre,
        totalChapters=req.totalChapters,
        wordsPerChapter=req.wordsPerChapter,
        createdAt=now_iso(),
        updatedAt=now_iso(),
    )
    write_json(os.path.join(get_novel_dir(novel_id), "metadata.json"), meta.model_dump())
    return meta


@router.get("/novels/{novel_id}", response_model=NovelMeta)
def get_novel(novel_id: str):
    """Get novel metadata."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    meta_path = os.path.join(get_novel_dir(novel_id), "metadata.json")
    meta = read_json(meta_path)
    if not meta:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return NovelMeta(**meta)


@router.put("/novels/{novel_id}", response_model=NovelMeta)
def update_novel(novel_id: str, meta: NovelMeta):
    """Update novel metadata."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    meta.updatedAt = now_iso()
    write_json(os.path.join(get_novel_dir(novel_id), "metadata.json"), meta.model_dump())
    return meta


@router.delete("/novels/{novel_id}")
def delete_novel(novel_id: str):
    """Delete a novel project."""
    import shutil
    novel_dir = get_novel_dir(novel_id)
    if os.path.isdir(novel_dir):
        shutil.rmtree(novel_dir)
    return {"ok": True}
