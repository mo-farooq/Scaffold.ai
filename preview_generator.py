#!/usr/bin/env python3
"""Interactive CLI tool to test dynamic milestone generation.

Usage
-----
    uv run python preview_generator.py "A command-line weather app in Python"
    uv run python preview_generator.py "A Redis-like key-value store in Go"
"""

from __future__ import annotations

import argparse
import sys

from scaffold.generator import generate_milestones

DEFAULT_PROJECT = (
    "A command-line weather application written in Python. "
    "Users can enter a city name to view current temperature, humidity, "
    "and 5-day forecast using the OpenWeather API."
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate learning milestones for a given project description.",
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=DEFAULT_PROJECT,
        help="Project description text (default: Weather CLI app example)",
    )
    args = parser.parse_args(argv)

    print("=" * 72)
    print("PROJECT DESCRIPTION")
    print("=" * 72)
    print(args.project)
    print()
    print("Generating milestones with Gemini 3.1 Flash Lite…")
    print()

    try:
        milestones = generate_milestones(args.project)
    except Exception as err:
        print(f"Error generating milestones: {err}", file=sys.stderr)
        sys.exit(1)

    print("=" * 72)
    print(f"GENERATED MILESTONES ({len(milestones)} items)")
    print("=" * 72)
    for i, m in enumerate(milestones, 1):
        print(f"{i}. {m}")
    print()


if __name__ == "__main__":
    main()
