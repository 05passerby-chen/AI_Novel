# backend/api/characters.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.character import Character
from services.file_service import get_novel_dir, read_json, write_json, generate_id, novel_exists, delete_file
import os

router = APIRouter()


def _characters_path(novel_id: str) -> str:
    return os.path.join(get_novel_dir(novel_id), "characters.json")


def _load_characters(novel_id: str) -> list[dict]:
    return read_json(_characters_path(novel_id), default=[])


def _save_characters(novel_id: str, chars: list[dict]) -> None:
    write_json(_characters_path(novel_id), chars)


@router.get("/novels/{novel_id}/characters", response_model=list[Character])
def list_characters(novel_id: str):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    chars = _load_characters(novel_id)
    return [Character(**c) for c in chars]


@router.post("/novels/{novel_id}/characters", response_model=Character)
def create_character(novel_id: str, char: Character):
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    chars = _load_characters(novel_id)
    char.id = generate_id()
    chars.append(char.model_dump())
    _save_characters(novel_id, chars)
    return char


@router.get("/novels/{novel_id}/characters/{char_id}", response_model=Character)
def get_character(novel_id: str, char_id: str):
    chars = _load_characters(novel_id)
    for c in chars:
        if c["id"] == char_id:
            return Character(**c)
    raise HTTPException(status_code=404, detail="Character not found")


@router.put("/novels/{novel_id}/characters/{char_id}", response_model=Character)
def update_character(novel_id: str, char_id: str, updated: Character):
    chars = _load_characters(novel_id)
    for i, c in enumerate(chars):
        if c["id"] == char_id:
            updated.id = char_id
            chars[i] = updated.model_dump()
            _save_characters(novel_id, chars)
            return updated
    raise HTTPException(status_code=404, detail="Character not found")


@router.delete("/novels/{novel_id}/characters/{char_id}")
def delete_character(novel_id: str, char_id: str):
    chars = _load_characters(novel_id)
    chars = [c for c in chars if c["id"] != char_id]
    _save_characters(novel_id, chars)
    return {"ok": True}
