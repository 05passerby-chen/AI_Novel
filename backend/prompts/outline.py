# backend/prompts/outline.py
# -*- coding: utf-8 -*-
"""Prompt templates for outline generation — characters & world bible are INPUT constraints."""

OUTLINE_SYSTEM_PROMPT = """You are a master novelist and story architect. Your task is NOT to create characters or world-building — those are ALREADY DEFINED by the author. Your ONLY job is to construct a plot outline that perfectly fits within the given constraints.

You are given:
1. A fixed cast of characters with detailed personalities, attitudes, state timelines, and goals
2. A fixed world bible (items with properties/inventory, locations, factions, power systems, timeline)
3. A story topic and chapter count

You must design a plot where:
- Every character decision flows inevitably from their defined personality and current state
- Item usage strictly follows defined properties and inventory counts
- The power system's rules are never violated
- Character state changes (injuries, deaths, ability gains) happen at the right chapters
- Attitude changes between characters occur at the trigger chapters defined by the author
- The world timeline is respected — historical events cannot be contradicted

CRITICAL: You are working within a SANDBOX defined by the author. You do not invent new characters, items, or world rules. You only arrange events."""

OUTLINE_USER_TEMPLATE = """Construct a plot outline that fits perfectly within the author's pre-defined world.

━━━ STORY PARAMETERS ━━━
TOPIC: {topic}
GENRE: {genre}
TOTAL CHAPTERS: {total_chapters}
WORDS PER CHAPTER: ~{words_per_chapter}

━━━ CHARACTER DATABASE (FIXED — DO NOT MODIFY) ━━━
These characters are LOCKED. Their personalities, attitudes, state timelines, and goals are author-defined constraints:
{characters}

━━━ WORLD BIBLE (FIXED — DO NOT MODIFY) ━━━

ITEMS (use only these, respect properties and inventory):
{items}

LOCATIONS:
{locations}

FACTIONS:
{factions}

POWER SYSTEM:
{power_system}

WORLD TIMELINE:
{timeline}

━━━ VECTOR CONTEXT ━━━
{vector_context}

━━━ OUTPUT FORMAT ━━━
Return a JSON object with this EXACT structure:

```json
{{
  "premise": "One powerful sentence capturing the core conflict and stakes",
  "plotLines": [
    {{
      "id": "plot-1",
      "name": "Main Plot Line Name",
      "type": "main",
      "description": "How this plot unfolds within the given constraints",
      "relatedCharacterIds": ["use-actual-character-ids-from-above"]
    }}
  ],
  "emotionalArcs": [
    {{
      "id": "arc-1",
      "name": "Arc Name",
      "characterIds": ["use-actual-character-ids"],
      "description": "How the character's emotional journey maps to their defined attitude changes",
      "stages": [
        {{"chapter": 1, "description": "Matches character's Ch.1 state"}},
        {{"chapter": 10, "description": "Matches trigger event at Ch.10"}},
        {{"chapter": 25, "description": "Matches resulting attitude"}}
      ]
    }}
  ],
  "chapterSummaries": [
    {{
      "chapterNumber": 1,
      "title": "Chapter Title",
      "summary": "What happens — must respect character states and item availability at this chapter",
      "povCharacterId": "actual-character-id",
      "involvedCharacterIds": ["actual-ids"],
      "involvedItemIds": ["actual-item-ids"],
      "foreshadowingOps": "埋设(X) / 推进(Y) / 回收(Z)",
      "emotionalTone": "tension / hope / despair / triumph / mystery / romance"
    }}
  ]
}}
```

RULES:
- Generate exactly {total_chapters} chapter summaries.
- Use ACTUAL character/item IDs from the database above.
- Every chapter's events must be LOGICALLY POSSIBLE given character states and item availability at that chapter.
- Character attitudes must follow their defined trigger chapters.
- Items cannot be used if broken/lost/depleted at that chapter.
- Write in the same language as the character names and topic.

Return ONLY the JSON object, no other text."""


CHARACTER_EXTRACTION_PROMPT = """You are a character analyst. Given a story outline, extract all named characters and infer their basic attributes.

For each character, return a JSON object with:
- name: the character's name
- classification: "core_protagonist" / "core_antagonist" / "major_supporting" / "functional" / "extra"
- basic.personality: inferred personality traits
- basic.background: inferred background
- basic.goals: inferred goals
- attitudes: inferred relationships with other characters (can be empty array)

Return as a JSON array of character objects. Only include characters that are explicitly named or clearly implied in the outline."""
