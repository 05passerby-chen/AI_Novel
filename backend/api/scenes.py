# backend/api/scenes.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.scene_card import SceneCard
from services.file_service import get_novel_dir, read_json, write_json, generate_id, novel_exists
import os

router = APIRouter()


def _path(novel_id: str) -> str:
    return os.path.join(get_novel_dir(novel_id), "scene_cards.json")


def _load(novel_id: str) -> list[dict]:
    return read_json(_path(novel_id), default=[])


def _save(novel_id: str, data: list[dict]) -> None:
    write_json(_path(novel_id), data)


@router.get("/novels/{novel_id}/scenes", response_model=list[SceneCard])
def list_scenes(novel_id: str):
    if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
    scenes = _load(novel_id)
    scenes.sort(key=lambda s: (s.get("chapterNumber", 0), s.get("order", 0)))
    return [SceneCard(**s) for s in scenes]


@router.post("/novels/{novel_id}/scenes", response_model=SceneCard)
def create_scene(novel_id: str, scene: SceneCard):
    if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
    data = _load(novel_id)
    scene.id = generate_id()
    scene.order = len([s for s in data if s.get("chapterNumber") == scene.chapterNumber])
    data.append(scene.model_dump())
    _save(novel_id, data)
    return scene


@router.put("/novels/{novel_id}/scenes/{scene_id}", response_model=SceneCard)
def update_scene(novel_id: str, scene_id: str, updated: SceneCard):
    data = _load(novel_id)
    for i, s in enumerate(data):
        if s["id"] == scene_id:
            updated.id = scene_id
            data[i] = updated.model_dump()
            _save(novel_id, data)
            return updated
    raise HTTPException(404, "Scene not found")


@router.put("/novels/{novel_id}/scenes/reorder")
def reorder_scenes(novel_id: str, body: dict):
    """Reorder scenes. body: { sceneIds: [...] }"""
    scene_ids: list[str] = body.get("sceneIds", [])
    data = _load(novel_id)
    for i, sid in enumerate(scene_ids):
        for s in data:
            if s["id"] == sid:
                s["order"] = i
    _save(novel_id, data)
    return {"ok": True}


@router.delete("/novels/{novel_id}/scenes/{scene_id}")
def delete_scene(novel_id: str, scene_id: str):
    data = _load(novel_id)
    data = [s for s in data if s["id"] != scene_id]
    _save(novel_id, data)
    return {"ok": True}
