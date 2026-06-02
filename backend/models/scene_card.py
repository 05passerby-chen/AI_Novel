# backend/models/scene_card.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Literal, Optional


class SceneCard(BaseModel):
    id: str = ""
    title: str = ""
    chapterNumber: int = 0
    status: Literal["idea", "outline", "draft", "done"] = "idea"
    order: int = 0                           # sort order within the chapter
    povCharacterId: Optional[str] = None
    goal: str = ""                           # scene goal
    conflict: str = ""                       # conflict type
    emotionalBeat: str = ""                  # emotional arc beat
    involvedCharacterIds: list[str] = Field(default_factory=list)
    involvedItemIds: list[str] = Field(default_factory=list)
    foreshadowingOps: str = ""               # planted/reinforced/resolved
    summary: str = ""
    hookToNext: str = ""                     # hook to next scene
