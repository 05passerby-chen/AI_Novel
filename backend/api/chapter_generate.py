# backend/api/chapter_generate.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.file_service import novel_exists, write_text, read_json, get_novel_dir
from services.chapter_service import generate_chapter
import os

router = APIRouter()


class GenerateChapterRequest(BaseModel):
    chapterNumber: int
    userGuidance: str = ""


@router.post("/novels/{novel_id}/chapters/{chapter_number}/generate")
def generate_chapter_endpoint(novel_id: str, chapter_number: int, req: GenerateChapterRequest | None = None):
    """Generate the full text for a chapter using AI."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    guidance = req.userGuidance if req else ""

    try:
        text = generate_chapter(
            novel_id=novel_id,
            chapter_number=chapter_number,
            user_guidance=guidance,
        )
        return {"content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
