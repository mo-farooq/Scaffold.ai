# ADR-007: Interactive TUI Application & Controller Pattern

* **Status**: Accepted
* **Date**: 2026-09-03
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

Scaffold.ai's engines (prompt, generator, session, evaluator, adapters, analytics, timeline) are fully built and tested, but only accessible through Python imports and preview scripts. Students need a standalone, immersive terminal application — not a collection of CLI commands — to experience the full learning journey.

---

## 2. Decision Drivers

* **Standalone Application**: A persistent, GUI-like terminal experience (similar to Claude Code).
* **Future Expansion**: Architecture must support future web UI, VS Code extension, or desktop app without rewriting business logic.
* **Rich Rendering**: AI responses with syntax-highlighted code blocks, markdown formatting, progress indicators.

---

## 3. Considered Options

* **Option 1**: `prompt_toolkit` + `rich` — manual layout, no built-in screen system.
* **Option 2**: `curses`/`blessed` — too low-level, no widget library.
* **Option 3**: **Textual** framework with a **Controller Pattern** separating UI from business logic.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3**. Textual TUI with UI-agnostic `ScaffoldController`.

### Architecture
- `ScaffoldController` (`src/scaffold/controller.py`): Pure business logic — no UI dependencies. Methods: `init_project()`, `send_message()`, `submit_answer()`, `get_status()`, `get_timeline()`.
- `ScaffoldApp` (`src/scaffold/tui/app.py`): Thin Textual presentation layer. Screens: Welcome, Setup, Session, Status.
- Future UIs (web, desktop) import `ScaffoldController` directly without touching TUI code.

### Positive Consequences
- Single `scaffold` command launches the full interactive experience.
- Controller is unit-testable without any UI framework.
- Adding new UI frontends requires zero changes to business logic.

---

## 5. Future Revisit Criteria

* Revisit when adding streaming response support (real-time token display).
* Revisit when building web UI — may need async controller methods.
