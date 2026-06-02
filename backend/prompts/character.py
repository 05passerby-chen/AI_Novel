# backend/prompts/character.py
# -*- coding: utf-8 -*-
"""Prompt for AI-generated character dynamics."""

CHARACTER_DYNAMICS_SYSTEM = """You are a professional character designer for novels. Given basic character information and the novel's topic, you will generate a complete set of dynamic (timeline-based) attributes for the character.

Each attribute is a list of chapter-indexed entries showing how the character evolves over time. Think carefully about:
- How their occupation might change (e.g. student → professional → leader)
- How their appearance changes with experiences
- How their personality evolves through challenges
- Goals that shift from immediate to long-term
- Secrets revealed at key moments
- Weaknesses that appear or are overcome

Return a JSON object with these fields. Each field is an array of {chapter, value} objects. Estimate reasonable chapter numbers based on the total chapter count."""

CHARACTER_DYNAMICS_USER = """Novel Topic: {topic}
Total Chapters: {total_chapters}

Character Basic Info:
- Name: {name}
- Classification: {classification}
- Gender: {gender}
- Age: {age}

Novel Genre: {genre}

Generate timeline-based dynamic attributes for this character. The character should evolve naturally across the {total_chapters} chapters.

Return ONLY a JSON object with this exact structure:
```json
{{
  "occupation": [{{"chapter": 1, "value": "..."}}, {{"chapter": 10, "value": "..."}}],
  "appearance": [{{"chapter": 1, "value": "..."}}, {{"chapter": 20, "value": "..."}}],
  "personality": [{{"chapter": 1, "value": "..."}}, {{"chapter": 15, "value": "..."}}],
  "behaviorHabits": [{{"chapter": 1, "value": "..."}}],
  "background": [{{"chapter": 1, "value": "..."}}, {{"chapter": 8, "value": "..."}}],
  "secrets": [{{"chapter": 1, "value": "..."}}, {{"chapter": 25, "value": "revealed..."}}],
  "weaknesses": [{{"chapter": 1, "value": "..."}}, {{"chapter": 12, "value": "..."}}],
  "longTermGoals": [{{"chapter": 1, "value": "..."}}],
  "shortTermGoals": [{{"chapter": 1, "value": "..."}}, {{"chapter": 5, "value": "..."}}]
}}
```
Provide 2-4 entries per field where meaningful change occurs. Write in Chinese if the character name is Chinese."""
