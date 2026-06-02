# backend/models/novel.py
# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional


class NovelMeta(BaseModel):
    id: str = ""
    title: str = ""
    author: str = "Author"
    topic: str = ""
    genre: str = ""
    totalChapters: int = 0
    wordsPerChapter: int = 3000
    createdAt: str = ""
    updatedAt: str = ""


class Chapter(BaseModel):
    number: int = 0
    title: str = ""
    content: str = ""
    status: str = "draft"  # draft | final


class AppSettings(BaseModel):
    deepseekApiKey: str = ""
    deepseekBaseUrl: str = "https://api.deepseek.com/v1"
    deepseekModel: str = "deepseek-chat"
    temperature: float = 0.7
    maxTokens: int = 4096


class CreateNovelRequest(BaseModel):
    title: str
    author: str = "Author"
    topic: str = ""
    genre: str = ""
    totalChapters: int = 30
    wordsPerChapter: int = 3000


class CreateChapterRequest(BaseModel):
    number: int
    title: str
    content: str = ""


class UpdateChapterRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class GenerateOutlineRequest(BaseModel):
    topic: str
    totalChapters: int = 30
    wordsPerChapter: int = 3000
