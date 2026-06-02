# backend/api/generate.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.novel import GenerateOutlineRequest
from models.outline import Outline
from services.file_service import get_novel_dir, read_json, write_json, novel_exists
from services.outline_service import generate_outline, extract_characters_from_text
from services.vector_service import index_characters
import os

router = APIRouter()


@router.post("/novels/{novel_id}/outline/generate", response_model=Outline)
def generate_novel_outline(novel_id: str, req: GenerateOutlineRequest | None = None):
    """Generate a complete story outline using DeepSeek."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    if req is None:
        # Read metadata for defaults
        meta = read_json(os.path.join(get_novel_dir(novel_id), "metadata.json"))
        req = GenerateOutlineRequest(
            topic=meta.get("topic", "A hero's journey"),
            totalChapters=meta.get("totalChapters", 30),
            wordsPerChapter=meta.get("wordsPerChapter", 3000),
        )

    # Update metadata
    meta = read_json(os.path.join(get_novel_dir(novel_id), "metadata.json"))
    if meta:
        meta["topic"] = req.topic
        meta["totalChapters"] = req.totalChapters
        meta["wordsPerChapter"] = req.wordsPerChapter
        write_json(os.path.join(get_novel_dir(novel_id), "metadata.json"), meta)

    characters_path = os.path.join(get_novel_dir(novel_id), "characters.json")
    world_bible_dir = os.path.join(get_novel_dir(novel_id), "items.json")
    outline_path = os.path.join(get_novel_dir(novel_id), "outline.json")

    outline = generate_outline(
        novel_id=novel_id,
        request=req,
        characters_json_path=characters_path,
        world_bible_dir=world_bible_dir,
        outline_path=outline_path,
    )

    # Save outline
    write_json(outline_path, outline.model_dump())

    return outline


@router.post("/novels/{novel_id}/vector/generate")
def generate_vector_store(novel_id: str):
    """Generate or regenerate the vector store from locked characters."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    characters_path = os.path.join(get_novel_dir(novel_id), "characters.json")
    characters = read_json(characters_path, default=[])

    if not characters:
        raise HTTPException(status_code=400, detail="No characters found. Create characters first.")

    # Only index locked characters, or all if none locked
    locked = [c for c in characters if c.get("locked")]
    chars_to_index = locked if locked else characters

    index_characters(novel_id, chars_to_index)

    return {
        "ok": True,
        "indexedCount": len(chars_to_index),
        "totalCharacters": len(characters),
        "onlyLocked": len(locked) > 0,
    }


@router.post("/novels/{novel_id}/outline/extract-characters")
def extract_characters(novel_id: str):
    """Extract character suggestions from the generated outline."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    outline_path = os.path.join(get_novel_dir(novel_id), "outline.json")
    outline_data = read_json(outline_path)

    if not outline_data:
        raise HTTPException(status_code=400, detail="No outline found. Generate an outline first.")

    # Convert outline to text for extraction
    import json
    outline_text = json.dumps(outline_data, ensure_ascii=False, indent=2)

    characters = extract_characters_from_text(outline_text)
    return {"characters": characters}


@router.post("/novels/{novel_id}/characters/{char_id}/generate-dynamics")
def generate_character_dynamics(novel_id: str, char_id: str):
    """AI-generate timeline-based dynamic attributes for a character."""
    if not novel_exists(novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    import json
    from services.llm_service import chat_completion, load_settings
    from prompts.character import CHARACTER_DYNAMICS_SYSTEM, CHARACTER_DYNAMICS_USER

    characters = read_json(os.path.join(get_novel_dir(novel_id), "characters.json"), default=[])
    char = next((c for c in characters if c.get("id") == char_id), None)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    meta = read_json(os.path.join(get_novel_dir(novel_id), "metadata.json"), default={})

    prompt = CHARACTER_DYNAMICS_USER.format(
        topic=meta.get("topic", ""),
        total_chapters=meta.get("totalChapters", 30),
        name=char.get("name", ""),
        classification=char.get("classification", ""),
        gender=char.get("basic", {}).get("gender", ""),
        age=char.get("basic", {}).get("age", "?"),
        genre=meta.get("genre", ""),
    )

    settings = load_settings()
    response = chat_completion(
        settings=settings,
        system_prompt=CHARACTER_DYNAMICS_SYSTEM,
        user_prompt=prompt,
        max_tokens=4096,
    )

    # Parse JSON from response
    try:
        text = response.strip()
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        data = json.loads(text)
        return data
    except Exception:
        return {"error": "Failed to parse AI response", "raw": response[:500]}
