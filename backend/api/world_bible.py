# backend/api/world_bible.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.world_bible import Item, Location, Faction, PowerSystem, TimelineEvent
from services.file_service import get_novel_dir, read_json, write_json, generate_id, novel_exists
import os

router = APIRouter()

# Generic CRUD helper
def _get_bible_path(novel_id: str, category: str) -> str:
    return os.path.join(get_novel_dir(novel_id), f"{category}.json")

def _load(novel_id: str, category: str) -> list[dict]:
    return read_json(_get_bible_path(novel_id, category), default=[])

def _save(novel_id: str, category: str, data: list[dict]) -> None:
    write_json(_get_bible_path(novel_id, category), data)

def _crud_routes(router: APIRouter, prefix: str, ModelClass, category: str):
    """Register standard CRUD routes for a bible category."""

    @router.get(f"/novels/{{novel_id}}/world-bible/{category}", response_model=list[ModelClass])
    def list_entries(novel_id: str):
        if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
        return [ModelClass(**e) for e in _load(novel_id, category)]

    @router.post(f"/novels/{{novel_id}}/world-bible/{category}", response_model=ModelClass)
    def create_entry(novel_id: str, entry: ModelClass):
        if not novel_exists(novel_id): raise HTTPException(404, "Novel not found")
        data = _load(novel_id, category)
        entry.id = generate_id()
        data.append(entry.model_dump())
        _save(novel_id, category, data)
        return entry

    @router.put(f"/novels/{{novel_id}}/world-bible/{category}/{{entry_id}}", response_model=ModelClass)
    def update_entry(novel_id: str, entry_id: str, updated: ModelClass):
        data = _load(novel_id, category)
        for i, e in enumerate(data):
            if e["id"] == entry_id:
                updated.id = entry_id
                data[i] = updated.model_dump()
                _save(novel_id, category, data)
                return updated
        raise HTTPException(404, "Entry not found")

    @router.delete(f"/novels/{{novel_id}}/world-bible/{category}/{{entry_id}}")
    def delete_entry(novel_id: str, entry_id: str):
        data = _load(novel_id, category)
        data = [e for e in data if e["id"] != entry_id]
        _save(novel_id, category, data)
        return {"ok": True}


# Register routes for each category
_crud_routes(router, "items", Item, "items")
_crud_routes(router, "locations", Location, "locations")
_crud_routes(router, "factions", Faction, "factions")
_crud_routes(router, "power", PowerSystem, "power")
_crud_routes(router, "timeline", TimelineEvent, "timeline")
