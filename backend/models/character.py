# backend/models/character.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class CharacterClassification(str, Enum):
    core_protagonist = "core_protagonist"
    core_antagonist = "core_antagonist"
    major_supporting = "major_supporting"
    functional = "functional"
    extra = "extra"


class TimelineEntry(BaseModel):
    """A chapter-indexed attribute entry, e.g. occupation changes over time."""
    chapter: int = 1
    value: str = ""


class AttitudeChange(BaseModel):
    targetId: str = ""
    initialAttitude: str = ""
    triggerEvent: str = ""
    triggerChapter: int = 1
    resultingAttitude: str = ""
    resultChapter: int = 1


class CharacterState(BaseModel):
    chapter: int = 1
    status: Literal["alive", "injured", "dying", "dead", "missing", "unknown"] = "alive"
    description: str = ""


class AbilityChange(BaseModel):
    chapter: int = 1
    ability: str = ""
    description: str = ""


class CharacterBasic(BaseModel):
    """Static fields that don't change over chapters."""
    gender: str = ""
    age: Optional[int] = None


class Character(BaseModel):
    id: str = ""
    name: str = "New Character"
    classification: CharacterClassification = CharacterClassification.major_supporting
    locked: bool = False
    basic: CharacterBasic = Field(default_factory=CharacterBasic)

    # ─── Timeline-based attributes (each entry = value at a chapter) ───
    occupation: list[TimelineEntry] = Field(default_factory=list)
    appearance: list[TimelineEntry] = Field(default_factory=list)
    personality: list[TimelineEntry] = Field(default_factory=list)
    behaviorHabits: list[TimelineEntry] = Field(default_factory=list)
    background: list[TimelineEntry] = Field(default_factory=list)
    secrets: list[TimelineEntry] = Field(default_factory=list)
    weaknesses: list[TimelineEntry] = Field(default_factory=list)
    longTermGoals: list[TimelineEntry] = Field(default_factory=list)
    shortTermGoals: list[TimelineEntry] = Field(default_factory=list)

    # ─── Existing timeline fields ───
    attitudes: list[AttitudeChange] = Field(default_factory=list)
    stateTimeline: list[CharacterState] = Field(default_factory=list)
    abilityTimeline: list[AbilityChange] = Field(default_factory=list)
