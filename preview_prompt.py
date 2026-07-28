#!/usr/bin/env python3
"""Quick CLI to eyeball the generated prompt.

Usage
-----
    uv run python preview_prompt.py                  # defaults to Todo-app example
    uv run python preview_prompt.py --milestone 2    # jump to milestone 2 (1-based)
"""

from __future__ import annotations

import argparse
import sys

from scaffold.prompt import MilestoneContext, build_prompt

# ── Hardcoded example ────────────────────────────────────────────────────

TODO_PROJECT = (
    "A command-line Todo application written in Python. "
    "The app lets users create, read, update, and delete tasks, "
    "with each task having a title, status, and optional due date. "
    "Data is persisted to a local JSON file."
)

TODO_MILESTONES = [
    "Data model — define the Task dataclass and a TodoList container",
    "CRUD API — functions to add, list, update, and delete tasks",
    "CLI interface — use argparse to expose the CRUD operations",
    "Persistence — read/write the task list to a JSON file",
]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Preview the Learning Mode prompt for a sample project.",
    )
    parser.add_argument(
        "-m",
        "--milestone",
        type=int,
        default=1,
        help="1-based milestone index (default: 1)",
    )
    args = parser.parse_args(argv)

    index = args.milestone - 1  # convert to 0-based
    if index < 0 or index >= len(TODO_MILESTONES):
        print(
            f"Error: milestone must be between 1 and {len(TODO_MILESTONES)}",
            file=sys.stderr,
        )
        sys.exit(1)

    ctx = MilestoneContext(
        project_description=TODO_PROJECT,
        milestones=TODO_MILESTONES,
        current_index=index,
    )
    print(build_prompt(ctx))


if __name__ == "__main__":
    main()
