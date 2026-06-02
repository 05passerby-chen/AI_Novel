# backend/api/settings.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from models.novel import AppSettings
from services.llm_service import load_settings, save_settings

router = APIRouter()


@router.get("/settings", response_model=AppSettings)
def get_settings():
    return load_settings()


@router.put("/settings", response_model=AppSettings)
def update_settings(settings: AppSettings):
    save_settings(settings)
    return settings
