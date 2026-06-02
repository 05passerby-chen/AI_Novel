# backend/api/foreshadowing.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.foreshadowing import Foreshadowing
from services.file_service import get_novel_dir, read_json, write_json, generate_id, novel_exists
import os

router = APIRouter()


def _path(novel_id: str) -> str:
    return os.path.join(get_novel_dir(novel_id), "foreshadowing.json")


def _load(novel_id: str) -> list[dict]:
    return read_json(_path(novel_id), default=[])


def _save(novel_id: str, data: list[dict]) -> None:
    write_json(_path(novel_id), data)


@router.get("/novels/{novel_id}/foreshadowing", response_model=list[Foreshadowing])
def list_foreshadowing(novel_id: str):
    if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
    return [Foreshadowing(**f) for f in _load(novel_id)]


@router.post("/novels/{novel_id}/foreshadowing", response_model=Foreshadowing)
def create_foreshadowing(novel_id: str, entry: Foreshadowing):
    if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
    data = _load(novel_id)
    entry.id = generate_id()
    data.append(entry.model_dump())
    _save(novel_id, data)
    return entry


@router.put("/novels/{novel_id}/foreshadowing/{entry_id}", response_model=Foreshadowing)
def update_foreshadowing(novel_id: str, entry_id: str, updated: Foreshadowing):
    data = _load(novel_id)
    for i, f in enumerate(data):
        if f["id"] == entry_id:
            updated.id = entry_id
            data[i] = updated.model_dump()
            _save(novel_id, data)
            return updated
    raise HTTPException(404, "Foreshadowing not found")


@router.delete("/novels/{novel_id}/foreshadowing/{entry_id}")
def delete_foreshadowing(novel_id: str, entry_id: str):
    data = _load(novel_id)
    data = [f for f in data if f["id"] != entry_id]
    _save(novel_id, data)
    return {"ok": True}
