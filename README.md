# Scaffold.ai — Learning Mode

A CLI tool that sits between a student and an AI coding agent, pacing development around **learning** instead of task completion.

## What it does (Milestone 1)

The prompt wrapper takes a project description, a list of milestones, and the current milestone index, and generates a structured system prompt that enforces the **Learning Mode protocol**:

1. **Explain first** — the goal of this milestone before writing any code
2. **Stay in scope** — implement only this milestone, nothing ahead
3. **One concept at a time** — no large code dumps
4. **Explain trade-offs** — reasoning + at least one rejected alternative
5. **End with reflection** — one reflective question, then stop

## Quick start

```bash
# Install dependencies
uv sync

# Preview the generated prompt (Todo-app example)
uv run python preview_prompt.py                # milestone 1
uv run python preview_prompt.py --milestone 3  # milestone 3

# Run tests
uv run pytest -v
```

## Project structure

```
src/scaffold/
  prompt.py          # MilestoneContext + build_prompt()
preview_prompt.py    # CLI for eyeballing the prompt output
tests/
  test_prompt.py     # 23 structural + validation tests
```

## Requirements

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager
