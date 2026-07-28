"""Dynamic Milestone Generator for Scaffold.ai.

Uses an LLM (Gemini API) to automatically decompose any student project
description into 3–5 logically paced learning milestones.
"""

from __future__ import annotations

import json
import os
import re
from typing import Sequence

from dotenv import load_dotenv
from google import genai
from google.genai import types


def _clean_json_text(text: str) -> str:
    """Strip markdown code fence wrappers from raw LLM output text."""
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def generate_milestones(
    project_description: str,
    api_key: str | None = None,
    model_name: str = "gemini-3.1-flash-lite",
) -> list[str]:
    """Decompose a project description into 3–5 learning milestones.

    Parameters
    ----------
    project_description:
        A plain text description of the project the student wants to build.
    api_key:
        Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
    model_name:
        The Gemini model to call (default: 'gemini-3.1-flash-lite').

    Returns
    -------
    list[str]
        A list of 3 to 5 milestone titles ordered logically by progression.

    Raises
    ------
    ValueError
        If project_description is empty, API key is missing, or response is invalid.
    """
    if not project_description or not project_description.strip():
        raise ValueError("project_description must not be empty")

    load_dotenv()
    resolved_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY")
    if not resolved_key or not resolved_key.strip():
        raise ValueError(
            "GEMINI_API_KEY is missing. Pass api_key or set GEMINI_API_KEY environment variable."
        )

    system_instruction = (
        "You are an expert computer science educator. Your task is to break down "
        "a student's software project description into a sequence of 3 to 5 clear, "
        "logically ordered learning milestones.\n\n"
        "Guidelines for milestone creation:\n"
        "1. Milestone 1 should focus on data structures, data models, or core schemas.\n"
        "2. Milestone 2 should focus on core business logic or internal API functions.\n"
        "3. Milestone 3 should focus on user interfaces, CLI commands, or external IO.\n"
        "4. Milestone 4/5 (if needed) should focus on persistence, integration, or edge cases.\n"
        "5. Each milestone must be a concise, actionable summary of what will be built.\n\n"
        "Output Format:\n"
        "You MUST respond ONLY with a valid JSON array of strings. Do not include any explanations or intro text.\n"
        'Example output: ["Data model — define Task and TodoList", "CRUD API — functions for task management", "CLI interface — argparse integration", "Persistence — save to JSON file"]'
    )

    user_prompt = (
        f"Decompose this student project into 3 to 5 learning milestones:\n\n"
        f'"{project_description.strip()}"'
    )

    client = genai.Client(api_key=resolved_key)
    
    # Configure JSON output
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,  # Low temperature for consistent structural output
        response_mime_type="application/json",
        response_schema=list[str],
    )

    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=config,
    )

    raw_text = response.text or ""
    cleaned_text = _clean_json_text(raw_text)

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse LLM milestone JSON response: {err}") from err

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list of milestones, got {type(data).__name__}")

    milestones = [str(m).strip() for m in data if str(m).strip()]

    if not (3 <= len(milestones) <= 6):
        raise ValueError(
            f"Expected between 3 and 6 milestones, but received {len(milestones)}: {milestones}"
        )

    return milestones
