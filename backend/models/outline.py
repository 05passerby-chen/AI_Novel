# backend/models/outline.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional


class PlotLine(BaseModel):
    id: str = ""
    name: str = ""
    type: str = "main"  # main | sub
    description: str = ""
    relatedCharacterIds: list[str] = Field(default_factory=list)


class EmotionalArcStage(BaseModel):
    chapter: int = 0
    description: str = ""


class EmotionalArc(BaseModel):
    id: str = ""
    name: str = ""
    characterIds: list[str] = Field(default_factory=list)
    description: str = ""
    stages: list[EmotionalArcStage] = Field(default_factory=list)


class ChapterSummary(BaseModel):
    chapterNumber: int = 0
    title: str = ""
    summary: str = ""
    povCharacterId: Optional[str] = None
    involvedCharacterIds: list[str] = Field(default_factory=list)
    involvedItemIds: list[str] = Field(default_factory=list)
    foreshadowingOps: str = ""
    emotionalTone: str = ""


class Outline(BaseModel):
    premise: str = ""
    plotLines: list[PlotLine] = Field(default_factory=list)
    emotionalArcs: list[EmotionalArc] = Field(default_factory=list)
    chapterSummaries: list[ChapterSummary] = Field(default_factory=list)
