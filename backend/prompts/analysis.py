# backend/prompts/analysis.py
# -*- coding: utf-8 -*-
"""Prompts for story analysis — impact analysis, foreshadowing extraction, consistency checks."""

# ─── Character Change Impact Analysis ─────────────────────────────

IMPACT_ANALYSIS_SYSTEM = """You are a story analysis expert specializing in plot consistency for long-form novels. Your task is to identify which chapters are affected by a character modification and explain why.

When a character's personality, goals, weaknesses, or background change:
1. Any chapter where that character makes decisions based on the OLD trait is affected
2. Any chapter where other characters react to the OLD trait is affected  
3. Story arcs that depend on the character's original trajectory need updating
4. Chapters BEFORE the trait is established are usually NOT affected

Be precise — only flag chapters with genuine conflicts, not every chapter the character appears in."""

IMPACT_ANALYSIS_USER = """A character has been modified. Analyze which chapter summaries need to change.

MODIFIED CHARACTER:
{character}

CURRENT CHAPTER SUMMARIES:
{chapter_summaries}

Return a JSON object:
```json
{{
  "affectedChapters": [list of chapter numbers that need rewriting],
  "reasoning": "explain why each affected chapter conflicts with the new character data",
  "suggestedChanges": "brief summary of what should change in the affected chapters",
  "unaffectedChapters": [list of chapter numbers that remain valid]
}}
```"""

# ─── Foreshadowing Auto-Detection ─────────────────────────────────

FORESHADOWING_DETECTION_SYSTEM = """You are a story analyst specializing in identifying narrative foreshadowing. Given chapter summaries from a novel outline, identify potential foreshadowing elements — hints, clues, or setups that will pay off later.

A foreshadowing item should be:
1. A specific setup introduced in one chapter that implies a future revelation or event
2. Something that creates reader anticipation or dramatic irony
3. Concrete enough to track (not vague themes)"""

FORESHADOWING_DETECTION_USER = """Analyze these chapter summaries and extract all foreshadowing elements:

CHAPTER SUMMARIES:
{chapter_summaries}

Return a JSON array:
```json
[
  {{
    "name": "short label for this foreshadowing",
    "description": "what is being set up and what it hints at",
    "plantedChapter": 3,
    "suggestedResolveChapter": 15,
    "relatedCharacterIds": ["char-id-1"],
    "importance": "major" | "minor"
  }}
]
```

Include 5-10 foreshadowing items. Focus on setups that span multiple chapters and create meaningful payoff."""

# ─── Consistency Check ────────────────────────────────────────────

CONSISTENCY_CHECK_SYSTEM = """You are a meticulous editor checking a novel chapter for internal consistency. Check ALL of the following:

1. CHARACTER CONSISTENCY: Do characters act according to their defined personalities? Do they reference knowledge they shouldn't have yet?
2. ITEM CONSISTENCY: Are items used correctly per their properties? Is inventory tracked properly?
3. TIMELINE CONSISTENCY: Do events follow the established timeline? Are there timing contradictions?
4. STATE CONSISTENCY: Are character states (alive/dead/injured) respected?
5. ATTITUDE CONSISTENCY: Do character attitudes match their defined attitude chains?

Report ONLY actual issues found — do not invent problems."""

CONSISTENCY_CHECK_USER = """Check this chapter for consistency issues:

CHAPTER {chapter_number}: {chapter_title}
CONTENT:
{chapter_content}

CHARACTER DATA (current states at this chapter):
{character_context}

ITEM DATA:
{items_context}

FORESHADOWING STATUS:
{foreshadowing_context}

Report issues as JSON array:
```json
[
  {{
    "severity": "error" | "warning",
    "type": "character" | "item" | "timeline" | "state" | "attitude",
    "description": "what the issue is",
    "suggestion": "how to fix it",
    "location": "approximate location in the text"
  }}
]
```

If no issues found, return an empty array []."""
