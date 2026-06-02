# backend/services/llm_service.py
# -*- coding: utf-8 -*-
"""DeepSeek (OpenAI-compatible) LLM adapter."""

import json
import os
from openai import OpenAI
from models.novel import AppSettings

SETTINGS_FILE = os.path.expanduser("~/.ai_novel_editor_settings.json")


def load_settings() -> AppSettings:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        return AppSettings(**data)
    return AppSettings()


def save_settings(settings: AppSettings) -> None:
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=2)


def create_client(settings: AppSettings) -> OpenAI:
    import httpx
    # Create a clean http client — bypasses the 'proxies' kwarg conflict
    # between newer httpx and older openai versions
    http_client = httpx.Client(
        base_url=settings.deepseekBaseUrl or "https://api.deepseek.com/v1",
        timeout=httpx.Timeout(120.0),
    )
    return OpenAI(
        api_key=settings.deepseekApiKey,
        base_url=settings.deepseekBaseUrl or "https://api.deepseek.com/v1",
        http_client=http_client,
    )


def chat_completion(
    settings: AppSettings,
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send a chat completion request and return the response text."""
    client = create_client(settings)

    response = client.chat.completions.create(
        model=settings.deepseekModel,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature if temperature is not None else settings.temperature,
        max_tokens=max_tokens if max_tokens is not None else settings.maxTokens,
    )

    return response.choices[0].message.content or ""
