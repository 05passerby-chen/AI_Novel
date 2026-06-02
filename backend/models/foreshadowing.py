# backend/models/foreshadowing.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Literal, Optional


class Foreshadowing(BaseModel):
    id: str = ""
    name: str = ""                         # short label, e.g. "张三的身世之谜"
    status: Literal["planted", "reinforced", "resolved"] = "planted"
    description: str = ""                  # full description of the foreshadowing
    plantedChapter: int = 0                # chapter where it was first introduced
    reinforcedChapters: list[int] = Field(default_factory=list)  # chapters where it was hinted again
    resolvedChapter: Optional[int] = None  # chapter where it pays off
    relatedCharacterIds: list[str] = Field(default_factory=list)
    relatedItemIds: list[str] = Field(default_factory=list)
    notes: str = ""                        # author's planning notes
