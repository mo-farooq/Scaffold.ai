#!/usr/bin/env python3
"""Benchmark script to measure latency against performance budgets for Scaffold.ai."""

from __future__ import annotations

import tempfile
import time

from scaffold.prompt import MilestoneContext, build_prompt
from scaffold.session import advance_milestone, init_session, load_session


def benchmark_prompt_generation() -> float:
    ctx = MilestoneContext(
        project_description="A command-line Todo application written in Python.",
        milestones=["1. Data model", "2. CRUD API", "3. CLI", "4. Persistence"],
        current_index=0,
    )
    start = time.perf_counter()
    for _ in range(100):
        _ = build_prompt(ctx)
    elapsed_ms = ((time.perf_counter() - start) / 100) * 1000
    return elapsed_ms


def benchmark_session_io() -> float:
    with tempfile.TemporaryDirectory() as tmp_dir:
        start = time.perf_counter()
        for _ in range(20):
            session = init_session("Test Project", ["M1", "M2"], session_dir=tmp_dir)
            _ = load_session(session_dir=tmp_dir)
            _ = advance_milestone(session, session_dir=tmp_dir)
        elapsed_ms = ((time.perf_counter() - start) / 20) * 1000
        return elapsed_ms


def main() -> None:
    print("=" * 60)
    print("SCAFFOLD.AI PERFORMANCE BENCHMARKS")
    print("=" * 60)

    prompt_ms = benchmark_prompt_generation()
    print(f"Prompt Generation Latency: {prompt_ms:.3f} ms (Budget: < 5.0 ms) -> {'PASS ✅' if prompt_ms < 5.0 else 'FAIL ❌'}")

    session_ms = benchmark_session_io()
    print(f"Session I/O Cycle Latency:  {session_ms:.3f} ms (Budget: < 10.0 ms) -> {'PASS ✅' if session_ms < 10.0 else 'FAIL ❌'}")

    print("=" * 60)


if __name__ == "__main__":
    main()
