# backend/api/chapters.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.novel import Chapter, CreateChapterRequest, UpdateChapterRequest
from services.file_service import get_novel_dir, read_json, write_json, read_text, write_text, novel_exists, now_iso
import os

router = APIRouter()


def _chapters_index_path(novel_id: str) -> str:
    return os.path.join(get_novel_dir(novel_id), "chapters", "_index.json")


def _chapter_content_path(novel_id: str, number: int) -> str:
    return os.path.join(get_novel_dir(novel_id), "chapters", f"{number:04d}.md")


def _load_index(novel_id: str) -> list[dict]:
    return read_json(_chapters_index_path(novel_id), default=[])


def _save_index(novel_id: str, index: list[dict]) -> None:
    write_json(_chapters_index_path(novel_id), index)


@router.get("/novels/{novel_id}/chapters", response_model=list[Chapter])
def list_chapters(novel_id: str):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    index = _load_index(novel_id)
    chapters = []
    for entry in index:
        content = read_text(_chapter_content_path(novel_id, entry["number"]))
        chapters.append(Chapter(**{**entry, "content": content}))
    return chapters


@router.post("/novels/{novel_id}/chapters", response_model=Chapter)
def create_chapter(novel_id: str, req: CreateChapterRequest):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    index = _load_index(novel_id)

    # Check if chapter number already exists
    for entry in index:
        if entry["number"] == req.number:
            raise HTTPException(status_code=409, detail=f"Chapter {req.number} already exists")

    entry = {"number": req.number, "title": req.title, "status": "draft"}
    index.append(entry)
    index.sort(key=lambda e: e["number"])
    _save_index(novel_id, index)
    write_text(_chapter_content_path(novel_id, req.number), req.content)

    return Chapter(**{**entry, "content": req.content})


@router.get("/novels/{novel_id}/chapters/{chapter_number}", response_model=Chapter)
def get_chapter(novel_id: str, chapter_number: int):
    index = _load_index(novel_id)
    for entry in index:
        if entry["number"] == chapter_number:
            content = read_text(_chapter_content_path(novel_id, chapter_number))
            return Chapter(**{**entry, "content": content})
    raise HTTPException(status_code=404, detail="Chapter not found")


@router.put("/novels/{novel_id}/chapters/{chapter_number}", response_model=Chapter)
@router.post("/novels/{novel_id}/chapters/{chapter_number}", response_model=Chapter)
def update_chapter(novel_id: str, chapter_number: int, req: UpdateChapterRequest):
    index = _load_index(novel_id)
    for i, entry in enumerate(index):
        if entry["number"] == chapter_number:
            if req.title is not None:
                entry["title"] = req.title
            if req.content is not None:
                write_text(_chapter_content_path(novel_id, chapter_number), req.content)
            _save_index(novel_id, index)
            content = read_text(_chapter_content_path(novel_id, chapter_number))
            return Chapter(**{**entry, "content": content})
    raise HTTPException(status_code=404, detail="Chapter not found")


@router.delete("/novels/{novel_id}/chapters/{chapter_number}")
def delete_chapter(novel_id: str, chapter_number: int):
    index = _load_index(novel_id)
    index = [e for e in index if e["number"] != chapter_number]
    _save_index(novel_id, index)
    content_path = _chapter_content_path(novel_id, chapter_number)
    if os.path.exists(content_path):
        os.remove(content_path)
    return {"ok": True}
