# backend/models/world_bible.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional


class Item(BaseModel):
    id: str = ""
    name: str = "New Item"
    type: str = "weapon"
    properties: str = ""
    ownerId: Optional[str] = None
    status: str = "intact"
    inventory: int = 1
    currentInventory: int = 1
    chapterAcquired: int = 0
    description: str = ""


class Location(BaseModel):
    id: str = ""
    name: str = ""
    type: str = ""
    factionId: Optional[str] = None
    description: str = ""
    features: str = ""


class Faction(BaseModel):
    id: str = ""
    name: str = ""
    stance: str = ""
    members: list[str] = Field(default_factory=list)
    description: str = ""
    goals: str = ""


class PowerSystem(BaseModel):
    id: str = ""
    name: str = ""
    ranks: list[str] = Field(default_factory=list)
    description: str = ""


class TimelineEvent(BaseModel):
    id: str = ""
    name: str = ""
    era: str = ""
    year: int = 0
    description: str = ""
    affects: list[str] = Field(default_factory=list)
