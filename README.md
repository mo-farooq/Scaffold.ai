# Scaffold.ai — Learn by Building. Build by Learning.

An interactive AI-powered learning harness that paces software engineering around **conceptual mastery** rather than passive code generation.

Built with Python 3.12+, Textual TUI, and multi-agent connectors (Gemini API & Claude Code CLI).

---

## 🌟 What Scaffold.ai Does

Scaffold.ai transforms AI coding agents from passive code generators into structured, Socratic engineering tutors:

1. **Dynamic Milestone Generator** (`scaffold.generator`): Decomposes any student project idea into 2–10 logically sequenced, adaptive milestones based on scope.
2. **Learning Mode Protocol Harness** (`scaffold.prompt`): Injects strict pedagogical constraints (explain first, stay in scope, one concept at a time, trade-offs, reflection question, completeness).
3. **Session State Machine & Local Storage** (`scaffold.session`): Manages project progression and state transitions in `.scaffold/session.json`.
4. **Student Reflection Evaluator** (`scaffold.evaluator`): Grades student reflection answers on conceptual comprehension and provides progressive hints on retries.
5. **Agent Adapter Layer** (`scaffold.adapters`): Provider-agnostic connectors supporting direct Gemini API calls and Claude Code CLI subprocess execution.
6. **Protocol Validator** (`scaffold.validator`): Programmatically scores agent output against all 6 protocol rules.
7. **Analytics & Learning Timeline** (`scaffold.analytics`, `scaffold.timeline`): Tracks pass rates, common mistakes, and concepts learned.
8. **Interactive Terminal Application** (`scaffold.tui`): A standalone, persistent GUI in the terminal powered by [Textual](https://textual.textualize.io/).

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

Set your Gemini API key in `.env`:
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

---

### 1. Launch the Interactive Terminal App

Type `scaffold` to launch the full GUI application in your terminal:

```bash
uv run scaffold

# Or as a module:
uv run python -m scaffold.tui
```

---

### 2. Launch the Developer Test Lab

An all-in-one interactive CLI playground to test any subsystem with presets or custom inputs:

```bash
uv run python scripts/test_lab.py
```

---

### 3. Run Quality Gates & Tests

```bash
# Run all quality gates (Ruff + Mypy + Benchmarks + 90 tests):
./scripts/verify.sh

# Run end-to-end full-stack simulation:
uv run python scripts/e2e_verify.py
```

---

## 📁 Repository Structure

```
Scaffold/
├── src/scaffold/
│   ├── controller.py       # UI-agnostic business logic controller
│   ├── prompt.py           # System prompt builder & 5 protocol rules
│   ├── generator.py        # Dynamic LLM milestone generator
│   ├── session.py          # State machine & local storage (.scaffold/)
│   ├── evaluator.py        # Student reflection answer grading engine
│   ├── validator.py        # Programmatic protocol compliance checker
│   ├── analytics.py        # Student attempts and pass rate analytics
│   ├── timeline.py         # Conceptual learning timeline recorder
│   ├── adapters/           # Multi-agent connectors (Gemini, Claude CLI)
│   └── tui/                # Textual interactive terminal application
├── docs/
│   ├── repository_navigation.md # Detailed orientation and architecture guide
│   ├── manual_testing_guide.md  # Step-by-step manual testing playbook
│   ├── definition_of_done.md    # 9-point quality DoD checklist
│   └── adr/                     # Architecture Decision Records (ADR-000 to ADR-007)
├── scripts/
│   ├── test_lab.py         # All-in-one developer testing playground
│   ├── verify.sh           # Unified CI/CD quality gate script
│   ├── benchmark.py        # Performance latency benchmarks
│   └── e2e_verify.py       # Headless end-to-end simulation
└── tests/                  # 90+ automated tests across all components
```

---

## 📚 Documentation Links

- 🧭 **[Repository Navigation Guide](docs/repository_navigation.md)** — Architectural map, directory orientation, and how to extend.
- 🧪 **[Manual Testing Guide](docs/manual_testing_guide.md)** — Comprehensive manual testing recipes and failure mode scenarios.
- 📐 **[Architecture Decision Records](docs/adr/)** — ADR-000 through ADR-007 detailing all engineering decisions.
- ✅ **[Definition of Done](docs/definition_of_done.md)** — Quality gates and engineering standards.

---

## 🛠️ Requirements

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- `GEMINI_API_KEY` set in `.env` or shell environment
