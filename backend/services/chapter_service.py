# backend/services/chapter_service.py
# -*- coding: utf-8 -*-
"""Chapter generation service — assembles context and calls DeepSeek."""

import json
import os
from models.novel import Chapter
from services.file_service import get_novel_dir, read_json, read_text
from services.llm_service import chat_completion, load_settings
from services.vector_service import build_context_for_chapter
from prompts.chapter import CHAPTER_SYSTEM_PROMPT, CHAPTER_USER_TEMPLATE


def generate_chapter(
    novel_id: str,
    chapter_number: int,
    user_guidance: str = "",
) -> str:
    """Generate the full text for a given chapter number."""
    settings = load_settings()
    novel_dir = get_novel_dir(novel_id)

    # Load chapter summary from outline
    outline = read_json(os.path.join(novel_dir, "outline.json"))
    chapter_summary_data = None
    if outline:
        for ch in outline.get("chapterSummaries", []):
            if ch.get("chapterNumber") == chapter_number:
                chapter_summary_data = ch
                break

    chapter_title = chapter_summary_data.get("title", f"Chapter {chapter_number}") if chapter_summary_data else f"Chapter {chapter_number}"
    chapter_summary = chapter_summary_data.get("summary", "") if chapter_summary_data else ""
    emotional_tone = chapter_summary_data.get("emotionalTone", "neutral") if chapter_summary_data else "neutral"

    # Get word count from metadata
    meta = read_json(os.path.join(novel_dir, "metadata.json"))
    word_count = meta.get("wordsPerChapter", 3000) if meta else 3000

    # Gather character context via vector store
    character_context = build_context_for_chapter(
        novel_id,
        f"Chapter {chapter_number}: {chapter_summary} - {emotional_tone}"
    )

    # Also load full character data
    characters = read_json(os.path.join(novel_dir, "characters.json"), default=[])
    if characters:
        char_summaries = []
        def _get_at_chapter(entries: list, ch: int) -> str:
            """Get the value of a timeline attribute at or before a given chapter."""
            applicable = sorted(
                [e for e in entries if e.get('chapter', 0) <= ch],
                key=lambda e: e.get('chapter', 0)
            )
            return applicable[-1].get('value', '') if applicable else ''

        for c in characters:
            parts = [f"{c.get('name', '')} ({c.get('classification', '')})"]
            parts.append(f"  Occupation: {_get_at_chapter(c.get('occupation', []), chapter_number)}")
            parts.append(f"  Personality: {_get_at_chapter(c.get('personality', []), chapter_number)}")
            parts.append(f"  Appearance: {_get_at_chapter(c.get('appearance', []), chapter_number)}")
            parts.append(f"  Long-term Goal: {_get_at_chapter(c.get('longTermGoals', []), chapter_number)}")
            parts.append(f"  Short-term Goal: {_get_at_chapter(c.get('shortTermGoals', []), chapter_number)}")
            # Current state at this chapter
            for state in c.get('stateTimeline', []):
                if state.get('chapter', 0) <= chapter_number:
                    parts.append(f"  Ch.{state.get('chapter')}: {state.get('status')} — {state.get('description', '')}")
            # Current attitudes
            for att in c.get('attitudes', []):
                if att.get('triggerChapter', 0) <= chapter_number:
                    effective = att.get('resultingAttitude') if att.get('resultChapter', 0) <= chapter_number else att.get('initialAttitude')
                    parts.append(f"  Attitude toward {att.get('targetId')}: {effective}")
            char_summaries.append('\n'.join(parts))
        character_context = '\n\n'.join(char_summaries) if char_summaries else character_context

    # Items context
    items = read_json(os.path.join(novel_dir, "items.json"), default=[])
    items_context = "No items defined."
    if items:
        item_lines = []
        for it in items:
            item_lines.append(
                f"- {it.get('name')}: type={it.get('type')}, status={it.get('status')}, "
                f"inventory={it.get('currentInventory')}/{it.get('inventory')}, "
                f"properties: {it.get('properties', 'N/A')}"
            )
        items_context = '\n'.join(item_lines)

    # Locations context
    locations = read_json(os.path.join(novel_dir, "locations.json"), default=[])
    locations_context = "No locations defined."
    if locations:
        locations_context = '\n'.join([f"- {l.get('name')}: {l.get('description', '')}" for l in locations])

    # Foreshadowing context
    foreshadowing = read_json(os.path.join(novel_dir, "foreshadowing.json"), default=[])
    foreshadowing_context = "No foreshadowing items to advance."
    if foreshadowing:
        active = [f for f in foreshadowing if f.get('status') in ('planted', 'reinforced')]
        if active:
            f_lines = []
            for f_item in active:
                f_lines.append(
                    f"- #{f_item.get('name')}: status={f_item.get('status')}, "
                    f"planted Ch.{f_item.get('plantedChapter')}, description: {f_item.get('description', '')}"
                )
            foreshadowing_context = '\n'.join(f_lines)

    # Previous chapter ending
    previous_ending = ""
    if chapter_number > 1:
        prev_content = read_text(os.path.join(novel_dir, "chapters", f"{chapter_number - 1:04d}.md"))
        if prev_content:
            # Take last ~500 chars as the ending hook
            previous_ending = prev_content[-500:] if len(prev_content) > 500 else prev_content

    # Build user prompt
    user_prompt = CHAPTER_USER_TEMPLATE.format(
        chapter_number=chapter_number,
        chapter_title=chapter_title,
        chapter_summary=chapter_summary,
        emotional_tone=emotional_tone,
        word_count=word_count,
        character_context=character_context or "No character data available.",
        items_context=items_context,
        locations_context=locations_context,
        foreshadowing_context=foreshadowing_context,
        previous_ending=previous_ending or "This is the first chapter.",
        user_guidance=user_guidance or "None",
    )

    # Call DeepSeek
    result = chat_completion(
        settings=settings,
        system_prompt=CHAPTER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=settings.maxTokens * 2,  # Allow longer output for chapters
    )

    return result
