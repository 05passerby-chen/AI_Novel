# backend/api/outline.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.outline import Outline
from services.file_service import get_novel_dir, read_json, write_json, novel_exists, now_iso
from services.outline_service import analyze_impact
import os

router = APIRouter()


def _outline_path(novel_id: str) -> str:
    return os.path.join(get_novel_dir(novel_id), "outline.json")


@router.get("/novels/{novel_id}/outline", response_model=Outline | None)
def get_outline(novel_id: str):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    data = read_json(_outline_path(novel_id))
    if data:
        return Outline(**data)
    return None


@router.put("/novels/{novel_id}/outline", response_model=Outline)
def save_outline(novel_id: str, outline: Outline):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    write_json(_outline_path(novel_id), outline.model_dump())
    return outline


@router.post("/novels/{novel_id}/outline/analyze-impact")
def analyze_character_impact(novel_id: str, body: dict):
    """Analyze how a character change affects the outline.
    
    Expected body:
    {
        "changedCharacter": { ... },
        "characters": [ ... ],
        "outline": { ... }
    }
    """
    result = analyze_impact(
        novel_id=novel_id,
        changed_character=body.get("changedCharacter", {}),
        characters=body.get("characters", []),
        outline=body.get("outline", {}),
    )
    return result
