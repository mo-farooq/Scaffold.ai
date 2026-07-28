#!/usr/bin/env python3
"""Live integration test: send the Learning Mode prompt to Gemini and inspect the response.

Usage
-----
    uv run python test_live.py

Requires GEMINI_API_KEY in .env or the shell environment.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from scaffold.prompt import MilestoneContext, build_prompt
from preview_prompt import TODO_PROJECT, TODO_MILESTONES


def main() -> None:
    # ── Load API key ─────────────────────────────────────────────────
    load_dotenv()  # reads .env if present
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Error: GEMINI_API_KEY not found. "
            "Set it in .env or export it in your shell.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Build the system prompt ──────────────────────────────────────
    ctx = MilestoneContext(
        project_description=TODO_PROJECT,
        milestones=TODO_MILESTONES,
        current_index=0,  # first milestone: data model
    )
    system_prompt = build_prompt(ctx)

    print("=" * 72)
    print("SYSTEM PROMPT (sent as system_instruction)")
    print("=" * 72)
    print(system_prompt)
    print()

    # ── Call Gemini API ──────────────────────────────────────────────
    user_message = "Let's start."

    print("=" * 72)
    print(f"USER MESSAGE: {user_message!r}")
    print("=" * 72)
    print()
    print("Calling Gemini 2.5 Flash…")
    print()

    # Try models in preference order — some may be unavailable or rate-limited.
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
    ]

    client = genai.Client(api_key=api_key)
    response = None

    for model_name in models_to_try:
        try:
            print(f"Trying {model_name}…")
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                ),
            )
            print(f"✅ Success with {model_name}\n")
            break
        except Exception as e:
            print(f"❌ {model_name} failed: {e!s:.120}\n")

    if response is None:
        print("All models failed. Check your API key and quota.", file=sys.stderr)
        sys.exit(1)

    print("=" * 72)
    print("MODEL RESPONSE")
    print("=" * 72)
    print(response.text)


if __name__ == "__main__":
    main()
