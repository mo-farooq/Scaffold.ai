# Scaffold.ai — Learning Mode CLI Harness

A CLI tool that sits between a student developer and an AI coding agent (e.g. Claude Code, Gemini), pacing development around **learning** instead of task completion.

---

## 🌟 What Scaffold.ai Does

### 1. Dynamic Milestone Generator (`scaffold.generate_milestones`)
Decomposes any raw student project idea string (e.g., *"A command-line weather app in Python"*) into 3–5 logically paced learning milestones using Gemini 3.1 Flash Lite with JSON schema enforcement.

### 2. Learning Mode System Prompt Harness (`scaffold.build_prompt`)
Constructs a structured system prompt that enforces the strict **Learning Mode Protocol**:
1. **Explain first** — Explain the goal of the milestone before writing code.
2. **Stay in scope** — Implement ONLY the current milestone.
3. **One concept at a time** — Use sequential step-by-step code blocks with clear explanations.
4. **Explain trade-offs** — Reason about choices and include at least one rejected alternative.
5. **End with reflection** — Implement all sub-items of the milestone, issue one reflective question, and stop.

---

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone git@github.com:mo-farooq/Scaffold.ai.git
cd Scaffold

# Install dependencies using uv
uv sync
```

### 1. Generate Milestones Dynamically
```bash
# Generate milestones for a custom project idea
uv run python preview_generator.py "A Redis-like in-memory key-value store in Python"
```

### 2. Preview System Prompt
```bash
# Preview prompt for Milestone 1
uv run python preview_prompt.py --milestone 1
```

### 3. Run Live Gemini API Prompt Execution
```bash
uv run python test_live.py
```

### 4. Run Test Suite
```bash
uv run pytest -v
```

---

## 📁 Project Structure

```
Scaffold/
├── src/
│   └── scaffold/
│       ├── __init__.py         # Package exports (generate_milestones, MilestoneContext, build_prompt)
│       ├── prompt.py           # System prompt engine & protocol rules
│       └── generator.py        # Dynamic LLM milestone generator
├── preview_generator.py        # CLI for testing milestone generation
├── preview_prompt.py           # CLI for eyeballing system prompt output
├── test_live.py                # Live integration test against Gemini API
└── tests/
    ├── test_prompt.py          # Structural & validation tests for prompt wrapper
    └── test_generator.py       # Unit & integration tests for milestone generator
```

---

## 🛠️ Requirements

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- `GEMINI_API_KEY` set in `.env` or shell environment
