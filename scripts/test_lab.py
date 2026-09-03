#!/usr/bin/env python3
"""Interactive Developer Test Lab & Playground for Scaffold.ai.

An all-in-one terminal harness that lets developers manually test, inspect,
and benchmark every subsystem of Scaffold.ai without remembering CLI arguments.

Usage:
    uv run python scripts/test_lab.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add src directory to path for direct imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from scaffold.adapters import get_adapter, list_available_adapters
from scaffold.analytics import AnalyticsEngine
from scaffold.evaluator import evaluate_answer
from scaffold.generator import generate_milestones
from scaffold.prompt import MilestoneContext, build_prompt
from scaffold.session import (
    advance_milestone,
    init_session,
    load_session,
    reset_session,
)
from scaffold.timeline import LearningTimeline
from scaffold.validator import validate_protocol

# ─── Terminal Formatting Helpers ──────────────────────────────────────────


def _cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m"


def _green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def _red(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m"


def _print_header(title: str) -> None:
    width = 72
    print("\n" + "=" * width)
    print(_bold(_cyan(f"  🔬 SCAFFOLD.AI TEST LAB: {title}")))
    print("=" * width)


def _pause() -> None:
    input(_dim("\nPress Enter to return to main menu..."))


# ─── Option 1: Milestone Generator ────────────────────────────────────────


def test_generator() -> None:
    _print_header("Dynamic Milestone Generator")
    print("Presets:")
    print("  [1] Simple Script:  Word frequency counter in Python")
    print("  [2] Moderate CLI:   Command-line weather app using OpenWeather API")
    print("  [3] Complex Web:    Full-stack e-commerce marketplace with FastAPI & PostgreSQL")
    print("  [4] Custom:         Enter your own project idea")

    choice = input("\nSelect an option [1-4] (default: 2): ").strip() or "2"
    if choice == "1":
        idea = "A simple Python script to calculate word frequencies in a text file"
    elif choice == "2":
        idea = "A command-line weather application in Python using OpenWeather API"
    elif choice == "3":
        idea = "A full-stack e-commerce marketplace with FastAPI, PostgreSQL, and Stripe"
    else:
        idea = input("Enter your custom project idea: ").strip()
        if not idea:
            idea = "A command-line task manager in Python"

    print(f"\n{_yellow('▶ Generating milestones for:')} {idea}")
    print(_dim("Calling Gemini API..."))

    t0 = time.perf_counter()
    try:
        milestones = generate_milestones(idea)
        elapsed = time.perf_counter() - t0
        print(
            f"\n{_green('✅ Generated')} {_bold(str(len(milestones)))} milestones in {elapsed:.2f}s:\n"
        )
        for i, m in enumerate(milestones, 1):
            print(f"  {_cyan(str(i))}. {m}")
    except Exception as err:  # noqa: BLE001
        print(f"\n{_red('❌ Generation failed:')} {err}")

    _pause()


# ─── Option 2: Prompt Engine ──────────────────────────────────────────────


def test_prompt_engine() -> None:
    _print_header("Learning Mode Prompt Engine")
    milestones = [
        "Define the weather data model",
        "Implement API client with error handling",
        "Build CLI interface with argument parsing",
    ]
    print("Milestone Context:")
    for i, m in enumerate(milestones, 1):
        print(f"  {i}. {m}")

    idx_input = input("\nSelect milestone to preview [1-3] (default: 1): ").strip() or "1"
    try:
        idx = max(0, min(len(milestones) - 1, int(idx_input) - 1))
    except ValueError:
        idx = 0

    ctx = MilestoneContext(
        project_description="A command-line weather app in Python using OpenWeather API",
        milestones=milestones,
        current_index=idx,
    )
    prompt = build_prompt(ctx)

    print(f"\n{_green('✅ Rendered System Prompt')} ({len(prompt)} chars):")
    print("-" * 72)
    print(prompt)
    print("-" * 72)

    _pause()


# ─── Option 3: Session State Machine ──────────────────────────────────────


def test_session_engine() -> None:
    _print_header("Session State Machine")
    scaffold_dir = PROJECT_ROOT / ".scaffold"
    session_file = scaffold_dir / "session.json"

    print("Current State on Disk:")
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  {_green('Active Session Found:')}")
            print(f"    Project:  {data.get('project_description')}")
            print(f"    State:    {data.get('state')}")
            print(
                f"    Current:  M{data.get('current_index', 0) + 1}: {data.get('current_milestone')}"
            )
            print(f"    Progress: {data.get('progress_percentage', 0):.1f}%")
        except Exception as err:  # noqa: BLE001
            print(f"  {_red('Corrupted session.json:')} {err}")
    else:
        print(f"  {_dim('No active session.json found in .scaffold/')}")

    print("\nActions:")
    print("  [1] Initialize fresh test session (Weather App, 3 milestones)")
    print("  [2] Advance to next milestone")
    print("  [3] Reset / delete session")
    print("  [4] Inspect raw JSON")
    print("  [5] Back to main menu")

    choice = input("\nSelect action [1-5]: ").strip()
    if choice == "1":
        milestones = [
            "Define the weather data model",
            "Implement API client with error handling",
            "Build CLI interface with argument parsing",
        ]
        s = init_session(
            "A command-line weather app in Python",
            milestones,
            session_dir=str(scaffold_dir),
        )
        print(f"{_green('✅ Session initialized:')} Current milestone: {s.current_milestone}")
    elif choice == "2":
        try:
            s = load_session(session_dir=str(scaffold_dir))
            s = advance_milestone(s, session_dir=str(scaffold_dir))
            print(
                f"{_green('✅ Advanced to:')} M{s.current_index + 1}: {s.current_milestone} ({s.progress_percentage:.1f}%)"
            )
        except Exception as err:  # noqa: BLE001
            print(f"{_red('❌ Failed to advance:')} {err}")
    elif choice == "3":
        reset_session(session_dir=str(scaffold_dir))
        print(f"{_green('✅ Session reset/deleted.')}")
    elif choice == "4":
        if session_file.exists():
            with open(session_file, "r", encoding="utf-8") as f:
                print("\n" + f.read())
        else:
            print(_yellow("No session.json file exists."))

    _pause()


# ─── Option 4: Reflection Evaluator ───────────────────────────────────────


def test_evaluator() -> None:
    _print_header("Student Reflection Evaluator")
    question = "Why did we choose a Python dataclass instead of a raw dictionary for our weather data model?"
    print(f"{_bold('Question:')} {question}\n")
    print("Choose test answer:")
    print("  [1] Strong Answer: 'Dataclasses give us attribute type safety...'")
    print("  [2] Weak Answer:   'Because dataclasses make the code run 10x faster...'")
    print("  [3] Custom Answer: Type your own answer")

    choice = input("\nSelect answer [1-3] (default: 1): ").strip() or "1"
    if choice == "1":
        answer = (
            "Dataclasses give us attribute type safety and autocomplete in the editor. "
            "If we misspell a key in a dictionary, it fails silently or throws a KeyError at runtime, "
            "whereas a dataclass catches typos immediately."
        )
    elif choice == "2":
        answer = "Because dataclasses make the Python code run 10x faster than dictionaries and save RAM."
    else:
        answer = input("\nEnter your answer: ").strip()
        if not answer:
            answer = "It gives better structure to our data."

    print(f'\n{_yellow("Student Answer:")}\n"{answer}"')
    print(_dim("\nEvaluating via Gemini API..."))

    t0 = time.perf_counter()
    try:
        res = evaluate_answer(
            student_answer=answer,
            question=question,
            milestone_title="Define the weather data model",
            project_description="A command-line weather app in Python",
        )
        elapsed = time.perf_counter() - t0

        status_str = _green("PASSED (ADVANCE)") if res.passed else _red("RETRY")
        print("\n" + "-" * 72)
        print(f"Outcome:   {status_str}")
        print(f"Score:     {res.score * 100:.1f}%")
        print(f"Latency:   {elapsed:.2f}s")
        print(f"Feedback:  {res.feedback}")
        if res.hint:
            print(f"Hint:      {_yellow(res.hint)}")
        print("-" * 72)
    except Exception as err:  # noqa: BLE001
        print(f"\n{_red('❌ Evaluation failed:')} {err}")

    _pause()


# ─── Option 5: Agent Adapters ─────────────────────────────────────────────


def test_adapters() -> None:
    _print_header("Agent Adapter Layer")
    adapters = list_available_adapters()
    print(f"Available Adapters: {adapters}")

    adapter_name = (
        input(f"\nChoose adapter [{' / '.join(adapters)}] (default: gemini): ").strip().lower()
        or "gemini"
    )
    msg = input("Enter test prompt (or press Enter for default): ").strip()
    if not msg:
        msg = "What is the very first thing we should code for our weather app data model?"

    system_prompt = (
        "You are an expert tutor following Scaffold.ai Learning Mode. "
        "Explain the goal first, stay in scope, explain trade-offs, and end with one reflective question."
    )

    print(f"\n{_yellow('▶ Sending to ' + adapter_name + ' adapter...')}")
    t0 = time.perf_counter()
    try:
        adapter = get_adapter(adapter_name)
        response = adapter.send_message(user_message=msg, system_prompt=system_prompt)
        elapsed = time.perf_counter() - t0

        print(
            f"\n{_green('✅ Response Received')} in {elapsed:.2f}s (Model: {response.model_name}):"
        )
        print("-" * 72)
        print(response.content[:1500])
        if len(response.content) > 1500:
            print(f"\n{_dim('... [truncated for display] ...')}")
        print("-" * 72)
    except Exception as err:  # noqa: BLE001
        print(f"\n{_red('❌ Adapter call failed:')} {err}")

    _pause()


# ─── Option 6: Protocol Validator ─────────────────────────────────────────


def test_protocol_validator() -> None:
    _print_header("Prompt Protocol Validator")
    sample_compliant = (
        "Welcome! The goal of Milestone 1 is to define our core data model.\n\n"
        "Here is the implementation:\n"
        "```python\n@dataclass\nclass WeatherReport:\n    city: str\n    temp: float\n```\n\n"
        "We chose a dataclass instead of a dictionary to gain compile-time type safety.\n\n"
        "### Milestone Check\n* [x] WeatherReport defined\n\n"
        "### 🤔 Reflective Question\nWhy is type safety advantageous when reading remote API payloads?"
    )

    print("Options:")
    print("  [1] Test Compliant Sample (All rules satisfied)")
    print("  [2] Test Non-Compliant Sample (Direct code dump with no reflection question)")
    print("  [3] Paste Custom Output Text")

    choice = input("\nSelect option [1-3] (default: 1): ").strip() or "1"
    if choice == "1":
        text = sample_compliant
    elif choice == "2":
        text = "Here is the code for the weather app:\n```python\nimport httpx\n```"
    else:
        print("Paste your response text (enter an empty line to finish):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        text = "\n".join(lines) or sample_compliant

    val = validate_protocol(text)
    status_str = _green("PASSED") if val.passed else _red("FAILED")
    print("\n" + "-" * 72)
    print(f"Validation Status:  {status_str}")
    print(f"Overall Score:      {val.overall_score * 100:.0f}%")
    print("\nDetailed Rule Checks:")
    for check in val.rule_checks:
        icon = _green("✅") if check.passed else _red("❌")
        print(f"  {icon} {_bold(check.rule_name)} (Score: {check.score:.1f}): {check.diagnostic}")
    print("-" * 72)

    _pause()


# ─── Option 7: Analytics & Timeline Inspector ─────────────────────────────


def test_analytics_and_timeline() -> None:
    _print_header("Analytics & Timeline Inspector")
    scaffold_dir = PROJECT_ROOT / ".scaffold"

    analytics = AnalyticsEngine(storage_dir=scaffold_dir)
    timeline = LearningTimeline(storage_dir=scaffold_dir)

    print(f"{_bold('📈 Reflection Analytics')} (.scaffold/analytics.json):")
    print(f"  Total Attempts:  {analytics.data.total_attempts}")
    print(f"  Passed:          {analytics.data.successful_evaluations}")
    print(f"  Failed:          {analytics.data.failed_evaluations}")
    print(f"  Pass Rate:       {analytics.data.pass_rate:.1f}%")
    print(f"  Total Time:      {analytics.data.total_duration_seconds:.1f}s")
    if analytics.data.common_mistakes:
        print(f"  Common Mistakes Recorded ({len(analytics.data.common_mistakes)}):")
        for m in analytics.data.common_mistakes[:3]:
            print(f"    - {_yellow(m)}")

    print(f"\n{_bold('📚 Learning Timeline')} (.scaffold/timeline.json):")
    if timeline.data.entries:
        for e in timeline.data.entries:
            icon = _green("✅") if e.reflection_outcome == "PASSED" else _red("🔄")
            print(
                f"  {icon} {_bold('M' + str(e.milestone_index + 1))}: {e.concept_learned} ({e.timestamp[:19]})"
            )
    else:
        print("  " + _dim("No timeline concepts recorded yet."))

    _pause()


# ─── Option 8: Launch Interactive TUI App ─────────────────────────────────


def launch_tui() -> None:
    _print_header("Launching Scaffold.ai Interactive TUI")
    print("Starting Textual Terminal Application...")
    time.sleep(1)
    try:
        subprocess.run(["uv", "run", "scaffold"], cwd=str(PROJECT_ROOT), check=False)
    except Exception as err:  # noqa: BLE001
        print(f"{_red('Failed to launch TUI:')} {err}")
        _pause()


# ─── Option 9: Run Automated Quality Gates ────────────────────────────────


def run_quality_gates() -> None:
    _print_header("Automated Quality Gates")
    print("Running scripts/verify.sh...")
    subprocess.run(["./scripts/verify.sh"], cwd=str(PROJECT_ROOT), check=False)
    print("\nRunning scripts/e2e_verify.py...")
    subprocess.run(
        ["uv", "run", "python", "scripts/e2e_verify.py"], cwd=str(PROJECT_ROOT), check=False
    )
    _pause()


# ─── Main Menu Loop ───────────────────────────────────────────────────────


def main() -> None:
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print("=" * 72)
        print(_bold(_cyan("         🔬 SCAFFOLD.AI — DEVELOPER TEST LAB & PLAYGROUND")))
        print("=" * 72)
        print("  [1] 🎯 Test Dynamic Milestone Generator (Preset or Custom Idea)")
        print("  [2] 📜 Test Learning Mode Prompt Engine (Inspect Rendered System Prompt)")
        print("  [3] 🔄 Test Session State Machine (Init, Advance, Reset, Inspect JSON)")
        print("  [4] 🧠 Test Reflection Evaluator (Evaluate Good vs Weak Answers Live)")
        print("  [5] 🔌 Test Agent Adapters (Send Test Message to Gemini or Claude CLI)")
        print("  [6] 🛡️  Test Prompt Protocol Validator (Score Responses Against 6 Rules)")
        print("  [7] 📊 Inspect Analytics & Learning Timeline (.scaffold/ Records)")
        print("  [8] 🚀 Launch Interactive TUI Application (Full Terminal Experience)")
        print("  [9] 🧪 Run All Automated Quality Gates (verify.sh + e2e_verify.py)")
        print("  [0] ❌ Exit Test Lab")
        print("=" * 72)

        choice = input(_bold("\nEnter selection [0-9]: ")).strip()
        if choice == "1":
            test_generator()
        elif choice == "2":
            test_prompt_engine()
        elif choice == "3":
            test_session_engine()
        elif choice == "4":
            test_evaluator()
        elif choice == "5":
            test_adapters()
        elif choice == "6":
            test_protocol_validator()
        elif choice == "7":
            test_analytics_and_timeline()
        elif choice == "8":
            launch_tui()
        elif choice == "9":
            run_quality_gates()
        elif choice == "0":
            print(_green("\nExiting Scaffold.ai Test Lab. Happy building! 👋\n"))
            break


if __name__ == "__main__":
    main()
