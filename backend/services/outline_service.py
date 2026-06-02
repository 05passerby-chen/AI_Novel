# backend/services/outline_service.py
# -*- coding: utf-8 -*-
"""Outline generation using DeepSeek — inspired by Snowflake Method."""

import json
from models.outline import Outline
from models.novel import AppSettings, GenerateOutlineRequest
from services.llm_service import chat_completion, load_settings
from services.vector_service import build_context_for_chapter, query_characters
from services.file_service import read_json, write_json
from prompts.outline import OUTLINE_SYSTEM_PROMPT, OUTLINE_USER_TEMPLATE, CHARACTER_EXTRACTION_PROMPT


def generate_outline(
    novel_id: str,
    request: GenerateOutlineRequest,
    characters_json_path: str,
    world_bible_dir: str,
    outline_path: str,
) -> Outline:
    """Generate a complete story outline."""
    settings = load_settings()

    # Gather character context from vector store
    vector_context = build_context_for_chapter(
        novel_id,
        f"Story theme: {request.topic}, {request.totalChapters} chapters"
    )

    # Load character data for the prompt
    characters_data = ""
    if characters_json_path:
        chars = read_json(characters_json_path)
        if chars:
            locked_chars = [c for c in chars if c.get("locked")]
            if locked_chars:
                characters_data = json.dumps(locked_chars, ensure_ascii=False, indent=2)

    # Load world bible data
    novel_dir = os.path.dirname(characters_json_path) if characters_json_path else ""
    items_data = json.dumps(read_json(os.path.join(novel_dir, "items.json"), default=[]), ensure_ascii=False, indent=2)
    locations_data = json.dumps(read_json(os.path.join(novel_dir, "locations.json"), default=[]), ensure_ascii=False, indent=2)
    factions_data = json.dumps(read_json(os.path.join(novel_dir, "factions.json"), default=[]), ensure_ascii=False, indent=2)
    power_data = json.dumps(read_json(os.path.join(novel_dir, "power.json"), default=[]), ensure_ascii=False, indent=2)
    timeline_data = json.dumps(read_json(os.path.join(novel_dir, "timeline.json"), default=[]), ensure_ascii=False, indent=2)

    # Build the user prompt
    user_prompt = OUTLINE_USER_TEMPLATE.format(
        topic=request.topic,
        genre=request.topic[:20],
        total_chapters=request.totalChapters,
        words_per_chapter=request.wordsPerChapter,
        characters=characters_data or "No locked characters defined yet.",
        items=items_data or "[]",
        locations=locations_data or "[]",
        factions=factions_data or "[]",
        power_system=power_data or "[]",
        timeline=timeline_data or "[]",
        vector_context=vector_context or "No vector context available.",
    )

    # Call DeepSeek
    raw_response = chat_completion(
        settings=settings,
        system_prompt=OUTLINE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=8192,
    )

    # Parse the JSON response
    outline = _parse_outline_response(raw_response)
    return outline


def _parse_outline_response(raw: str) -> Outline:
    """Extract JSON from LLM response and parse into Outline model."""
    # The LLM should return JSON, possibly wrapped in ```json blocks
    text = raw.strip()

    # Try to extract from code fences
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()

    try:
        data = json.loads(text)
        return Outline(**data)
    except (json.JSONDecodeError, Exception):
        # Fallback: try to parse the raw text more loosely
        pass

    # If parsing fails, return a basic outline with the raw text as premise
    return Outline(
        premise=raw[:500],
        plotLines=[],
        emotionalArcs=[],
        chapterSummaries=[],
    )


def extract_characters_from_text(text: str) -> list[dict]:
    """Use DeepSeek to extract character information from generated outline."""
    settings = load_settings()
    response = chat_completion(
        settings=settings,
        system_prompt=CHARACTER_EXTRACTION_PROMPT,
        user_prompt=f"Extract all characters from the following story outline:\n\n{text}",
        max_tokens=4096,
    )
    # Try to parse the response as a list of character objects
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
        return json.loads(text)
    except Exception:
        return []


def analyze_impact(
    novel_id: str,
    changed_character: dict,
    characters: list[dict],
    outline: dict,
) -> dict:
    """Analyze which parts of the outline are affected by a character change."""
    settings = load_settings()

    # Build a prompt that asks DeepSeek to identify affected sections
    analysis_prompt = f"""
    A character has been modified:
    
    Character: {json.dumps(changed_character, ensure_ascii=False, indent=2)}
    
    Current outline chapter summaries:
    {json.dumps(outline.get('chapterSummaries', []), ensure_ascii=False, indent=2)}
    
    Analyze which chapter summaries would need to change because of this character modification.
    Return a JSON object:
    {{
        "affectedChapters": [list of chapter numbers],
        "reasoning": "explanation of why each chapter is affected",
        "suggestedChanges": "brief description of what should change"
    }}
    """
    
    response = chat_completion(
        settings=settings,
        system_prompt="You are a story analysis expert. Your task is to identify plot impacts from character changes.",
        user_prompt=analysis_prompt,
        max_tokens=2048,
    )
    
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
        return json.loads(text)
    except Exception:
        return {"affectedChapters": [], "reasoning": "Could not parse impact analysis", "suggestedChanges": ""}
