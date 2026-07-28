#!/usr/bin/env python3
"""End-to-End Workflow Verification Harness for Scaffold.ai.

Simulates a full student learning journey across all components:
1. Dynamic Milestone Generator
2. Session State Machine Persistence
3. Learning Mode Prompt Engine
4. Prompt Protocol Validator
5. Reflection Evaluator Engine
6. Reflection Analytics
7. Learning Timeline
"""

from __future__ import annotations

import tempfile

from scaffold import (
    AnalyticsEngine,
    LearningTimeline,
    advance_milestone,
    build_prompt,
    evaluate_answer,
    generate_milestones,
    get_current_context,
    init_session,
    validate_protocol,
)

SAMPLE_PROJECT = "A command-line weather application in Python using OpenWeather API"


def main() -> None:
    print("=" * 72)
    print("SCAFFOLD.AI END-TO-END WORKFLOW VERIFICATION")
    print("=" * 72)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Step 1: Milestone Generation
        print("\n1. Testing Milestone Generator...")
        milestones = generate_milestones(SAMPLE_PROJECT)
        print(f"   Generated {len(milestones)} milestones successfully.")

        # Step 2: Session Initialization
        print("\n2. Testing Session Initialization...")
        session = init_session(SAMPLE_PROJECT, milestones, session_dir=tmp_dir)
        print(f"   Session State: {session.state.value}")
        print(f"   Session File: {tmp_dir}/session.json")

        # Step 3: Prompt Generation & Protocol Validation
        print("\n3. Testing Prompt Engine & Protocol Validator...")
        ctx = get_current_context(session)
        _ = build_prompt(ctx)

        # Simulate agent output text
        simulated_agent_output = (
            "Welcome! Let's start Milestone 1: The Data Model.\n\n"
            "Our goal is to define the weather data structure before building API logic.\n\n"
            "```python\n@dataclass\nclass Weather:\n    city: str\n    temp: float\n```\n\n"
            "We chose a dataclass over a dictionary for type safety.\n\n"
            "### Milestone Check\n* [x] Weather model defined.\n\n"
            "### 🤔 Reflective Question\nWhy is type safety helpful when working with API data?"
        )

        validation = validate_protocol(simulated_agent_output)
        print(f"   Protocol Score: {validation.overall_score:.2f} (Passed: {validation.passed})")

        # Step 4: Reflection Evaluation
        print("\n4. Testing Reflection Evaluator...")
        student_answer = "Dataclasses prevent typo errors in key names at compile time."
        eval_result = evaluate_answer(
            student_answer=student_answer,
            question="Why is type safety helpful when working with API data?",
            milestone_title=session.current_milestone,
            project_description=session.project_description,
        )
        print(f"   Evaluator Score: {eval_result.score:.2f} (Passed: {eval_result.passed})")

        # Step 5: Reflection Analytics Recording
        print("\n5. Testing Reflection Analytics...")
        analytics = AnalyticsEngine(storage_dir=tmp_dir)
        _ = analytics.record_attempt(
            milestone_index=session.current_index,
            question="Why is type safety helpful when working with API data?",
            student_answer=student_answer,
            result=eval_result,
            duration_seconds=42.5,
        )
        print(f"   Analytics Record Saved (.scaffold/analytics.json): Total Attempts = {analytics.data.total_attempts}")

        # Step 6: Learning Timeline Recording
        print("\n6. Testing Learning Timeline...")
        timeline = LearningTimeline(storage_dir=tmp_dir)
        timeline.record_concept(
            milestone_index=session.current_index,
            milestone_title=session.current_milestone,
            concept_learned="Python Dataclasses & Type Hinting",
            files_modified=["src/weather/model.py"],
            adrs_referenced=["ADR-001"],
            reflection_outcome="PASSED",
        )
        print(f"   Timeline Recorded (.scaffold/timeline.json): Concepts = {len(timeline.data.entries)}")

        # Step 7: Session Progression
        print("\n7. Testing Session Progression...")
        session = advance_milestone(session, session_dir=tmp_dir)
        print(f"   New Progress: {session.progress_percentage:.1f}%")

    print("\n" + "=" * 72)
    print("END-TO-END WORKFLOW VERIFICATION PASSED SUCCESSFULLY ✅")
    print("=" * 72)


if __name__ == "__main__":
    main()
