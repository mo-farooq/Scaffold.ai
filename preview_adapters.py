#!/usr/bin/env python3
"""Interactive Preview CLI for the Scaffold.ai Agent Adapter Layer.

Demonstrates prompt injection and execution through the adapter layer.

Usage:
    uv run python preview_adapters.py
    uv run python preview_adapters.py --adapter claude
"""

from __future__ import annotations

import argparse
import sys

from scaffold.adapters import get_adapter, list_available_adapters
from scaffold.prompt import MilestoneContext, build_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold.ai Adapter Layer Preview")
    parser.add_argument(
        "--adapter",
        type=str,
        default="gemini",
        help=f"Adapter to use. Available: {', '.join(list_available_adapters())}",
    )
    parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Custom user message to send (defaults to interactive mode).",
    )
    args = parser.parse_args()

    print("=" * 68)
    print("SCAFFOLD.AI — AGENT ADAPTER LAYER PREVIEW")
    print("=" * 68)
    print(f"\nAvailable adapters: {list_available_adapters()}")
    print(f"Selected adapter:   {args.adapter}\n")

    # Build a sample Learning Mode system prompt
    ctx = MilestoneContext(
        project_description="A command-line weather app in Python using OpenWeather API",
        milestones=[
            "Define the Weather data model",
            "Implement API client with error handling",
            "Build CLI interface with argument parsing",
        ],
        current_index=0,
    )
    system_prompt = build_prompt(ctx)
    print(f"System Prompt Length: {len(system_prompt)} chars")
    print("-" * 68)

    # Get user message
    if args.message:
        user_message = args.message
    else:
        print("\nEnter your message to the agent (or press Enter for default):")
        user_message = input("> ").strip()
        if not user_message:
            user_message = "Let's start building! What should we do first for this milestone?"

    print(f"\nUser Message: {user_message[:120]}...")
    print("-" * 68)

    # Send through adapter
    try:
        adapter = get_adapter(args.adapter)
        print(f"\n🔄 Sending to {adapter.adapter_name} adapter...")
        response = adapter.send_message(
            user_message=user_message,
            system_prompt=system_prompt,
        )

        print(f"\n✅ Response received in {response.latency_seconds:.2f}s")
        print(f"   Model: {response.model_name}")
        print(f"   Content length: {len(response.content)} chars")
        print("-" * 68)
        print("\n📝 AGENT RESPONSE:\n")
        print(response.content[:2000])
        if len(response.content) > 2000:
            print(f"\n... [truncated, {len(response.content) - 2000} chars remaining]")

    except (ValueError, RuntimeError) as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 68)
    print("PREVIEW COMPLETE ✅")
    print("=" * 68)


if __name__ == "__main__":
    main()
