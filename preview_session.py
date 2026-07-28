#!/usr/bin/env python3
"""Interactive CLI preview for Scaffold.ai Session State Machine.

Usage
-----
    uv run python preview_session.py
"""

from __future__ import annotations

import tempfile
from scaffold import (
    advance_milestone,
    build_prompt,
    generate_milestones,
    get_current_context,
    init_session,
    load_session,
    reset_session,
)

SAMPLE_PROJECT = "A command-line weather application in Python using OpenWeather API"


def main() -> None:
    print("=" * 72)
    print("SCAFFOLD.AI SESSION STATE MACHINE DEMO")
    print("=" * 72)

    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f"\n1. Generating milestones for project: '{SAMPLE_PROJECT}'...")
        milestones = generate_milestones(SAMPLE_PROJECT)
        print("   Generated Milestones:")
        for i, m in enumerate(milestones, 1):
            print(f"   {i}. {m}")

        print(f"\n2. Initializing new session in temporary dir: {tmp_dir}")
        session = init_session(SAMPLE_PROJECT, milestones, session_dir=tmp_dir)
        print(f"   Status: {session.state.value}")
        print(f"   Current Milestone: {session.current_milestone}")
        print(f"   Progress: {session.progress_percentage:.1f}%")

        print("\n3. Loading session back from disk (.scaffold/session.json)...")
        loaded_session = load_session(session_dir=tmp_dir)
        print(f"   Loaded Project: '{loaded_session.project_description}'")
        print(f"   Loaded Milestone Index: {loaded_session.current_index}")

        print("\n4. Building system prompt from session context...")
        ctx = get_current_context(loaded_session)
        prompt = build_prompt(ctx)
        print(f"   Generated Prompt Length: {len(prompt)} characters")
        print("   Prompt Title Header:")
        print("   " + prompt.splitlines()[0])

        print("\n5. Advancing milestone step-by-step...")
        while not session.is_completed:
            print(
                f"   [Step {session.current_index + 1}/{len(session.milestones)}] "
                f"Working on: '{session.current_milestone}'"
            )
            session = advance_milestone(session, session_dir=tmp_dir)

        print(f"\n6. All Milestones Completed!")
        print(f"   Final State: {session.state.value}")
        print(f"   Final Progress: {session.progress_percentage:.1f}%")

        print("\n7. Resetting session...")
        reset_result = reset_session(session_dir=tmp_dir)
        print(f"   Session file removed: {reset_result}")

    print("\n" + "=" * 72)
    print("SESSION STATE MACHINE DEMO COMPLETE ✅")
    print("=" * 72)


if __name__ == "__main__":
    main()
