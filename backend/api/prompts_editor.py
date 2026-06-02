# backend/api/prompts_editor.py
# -*- coding: utf-8 -*-
"""API for reading and editing AI prompt templates — returns clean prompt text, not Python code."""
import os
import re
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

PROMPT_FILES = {
    "outline": "outline.py",
    "chapter": "chapter.py",
    "character": "character.py",
    "analysis": "analysis.py",
}


def _extract_prompts(filepath: str) -> dict[str, str]:
    """Parse a .py file and extract all triple-quoted string variable assignments.
    Returns {VAR_NAME: string_content}."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    result = {}
    # Match: VAR_NAME = """..."""  or  VAR_NAME = '''...'''
    pattern = r'^(\w+)\s*=\s*("""|\'\'\')(.*?)\2'
    for match in re.finditer(pattern, source, re.DOTALL | re.MULTILINE):
        name = match.group(1)
        content = match.group(3)
        # Remove leading newline after opening quotes
        if content.startswith('\n'):
            content = content[1:]
        result[name] = content

    return result


def _rebuild_file(filepath: str, prompts: dict[str, str]) -> None:
    """Rebuild a .py file from extracted prompts, preserving the file header comment."""
    # Read original to preserve header (everything before first assignment)
    original = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

    # Extract header (lines before first triple-quoted assignment)
    header_end = 0
    first_match = re.search(r'^\w+\s*=\s*("""|\'\'\')', original, re.MULTILINE)
    if first_match:
        # Find the start of this line
        line_start = original.rfind('\n', 0, first_match.start())
        header_end = line_start + 1 if line_start >= 0 else 0

    header = original[:header_end].rstrip()

    # Rebuild
    lines = [header] if header else ["# Auto-generated prompt file"]
    lines.append("")
    for name, content in prompts.items():
        lines.append(f'{name} = """')
        lines.append(content)
        lines.append('"""')
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))


@router.get("/prompts")
def list_prompts():
    """Return all prompt categories with their prompt texts (not raw Python)."""
    result = {}
    for name, filename in PROMPT_FILES.items():
        filepath = os.path.join(PROMPTS_DIR, filename)
        if os.path.exists(filepath):
            prompts = _extract_prompts(filepath)
            result[name] = {
                "filename": filename,
                "prompts": prompts,  # {VAR_NAME: text, ...}
            }
    return result


class UpdatePromptRequest(BaseModel):
    prompts: dict[str, str]  # {VAR_NAME: new_text, ...}


@router.put("/prompts/{name}")
def update_prompt(name: str, req: UpdatePromptRequest):
    """Save updated prompt texts for a category."""
    if name not in PROMPT_FILES:
        return {"error": f"Unknown prompt: {name}"}

    filepath = os.path.join(PROMPTS_DIR, PROMPT_FILES[name])
    # Merge with existing prompts (only update the ones provided)
    existing = _extract_prompts(filepath) if os.path.exists(filepath) else {}
    existing.update(req.prompts)
    _rebuild_file(filepath, existing)

    return {"ok": True, "name": name}


class GeneratePromptRequest(BaseModel):
    name: str
    prompt_key: str  # e.g. "OUTLINE_SYSTEM_PROMPT"
    description: str


@router.post("/prompts/generate")
def generate_prompt(req: GeneratePromptRequest):
    """Use AI to generate/improve a prompt template."""
    from services.llm_service import chat_completion, load_settings

    settings = load_settings()

    system = """You are an expert at writing AI prompts for novel generation. Write a clear, well-structured prompt that produces high-quality results.

The prompt should be plain text (not Python code). Use {placeholder} syntax for dynamic values.

Focus on:
1. Clear role definition for the AI
2. Specific, actionable rules
3. Structured output format requirements
4. Constraint enforcement
5. Language consistency"""

    user = f"""Write a prompt for a novel generator. The prompt is for: {req.prompt_key}

Requirements: {req.description}

Return ONLY the prompt text, no explanations, no markdown formatting. Use {{variable}} syntax for any dynamic placeholders."""

    response = chat_completion(
        settings=settings,
        system_prompt=system,
        user_prompt=user,
        max_tokens=2048,
    )

    return {"content": response.strip()}
