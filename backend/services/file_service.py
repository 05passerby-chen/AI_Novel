# backend/services/file_service.py
# -*- coding: utf-8 -*-
"""File I/O operations for the novel project structure."""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

NOVELS_DIR = os.path.expanduser("~/Novels")


def _ensure_novels_dir():
    os.makedirs(NOVELS_DIR, exist_ok=True)


def get_novel_dir(novel_id: str) -> str:
    return os.path.join(NOVELS_DIR, novel_id)


def novel_exists(novel_id: str) -> bool:
    return os.path.isdir(get_novel_dir(novel_id))


def init_novel_structure(novel_id: str) -> None:
    """Create the directory structure for a new novel."""
    base = get_novel_dir(novel_id)
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, "chapters"), exist_ok=True)
    os.makedirs(os.path.join(base, "characters"), exist_ok=True)


def read_json(filepath: str, default=None):
    if not os.path.exists(filepath):
        return default
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str, data) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_text(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_text(filepath: str, content: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def delete_file(filepath: str) -> None:
    if os.path.exists(filepath):
        os.remove(filepath)


def generate_id() -> str:
    return uuid.uuid4().hex[:12]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
