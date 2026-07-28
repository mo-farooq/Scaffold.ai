#!/usr/bin/env python3
"""Interactive CLI tool to test student reflection answer evaluation.

Usage
-----
    uv run python preview_evaluator.py
"""

from __future__ import annotations

import sys
from scaffold.evaluator import evaluate_answer

SAMPLE_QUESTION = (
    "If we decided later that every task needs a unique ID (like 1, 2, 3), "
    "how would using a dataclass make it easier to manage that change "
    "compared to using a simple dictionary?"
)

# Test answers representing different levels of student understanding
TEST_ANSWERS = [
    (
        "Strong Answer",
        "With a dataclass, we just add `id: int` to the class definition and Python enforces "
        "it everywhere. With a dictionary, we would have to hunt through all our code to update "
        "dictionary keys and hope we didn't miss any place where task dictionaries are created."
    ),
    (
        "Confused / Weak Answer",
        "Because dataclasses make the code run 10x faster than dictionaries."
    ),
]


def main() -> None:
    print("=" * 72)
    print("SCAFFOLD.AI REFLECTION EVALUATOR DEMO")
    print("=" * 72)
    print(f"\nREFLECTIVE QUESTION:\n\"{SAMPLE_QUESTION}\"\n")

    for label, answer in TEST_ANSWERS:
        print("-" * 72)
        print(f"TESTING STUDENT ANSWER [{label}]:")
        print(f"\"{answer}\"")
        print("\nGrading answer with Gemini 3.1 Flash Lite...")

        try:
            result = evaluate_answer(
                student_answer=answer,
                question=SAMPLE_QUESTION,
                milestone_title="Data Model",
                project_description="A command-line Todo app in Python",
            )
        except Exception as err:
            print(f"Error during evaluation: {err}", file=sys.stderr)
            continue

        print("\nEVALUATION RESULT:")
        print(f"  Passed: {result.passed}")
        print(f"  Score: {result.score:.2f}")
        print(f"  Suggested Action: {result.suggested_action}")
        print(f"  Feedback: {result.feedback}")
        if result.hint:
            print(f"  Hint: {result.hint}")
        print()

    print("=" * 72)
    print("REFLECTION EVALUATOR DEMO COMPLETE ✅")
    print("=" * 72)


if __name__ == "__main__":
    main()
