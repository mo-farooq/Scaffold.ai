# Scaffold.ai — Engineering Decision Log

This log records major technical observations, problem statements, decisions, and rationales adopted during the development of Scaffold.ai.

---

## Log Entries

### Entry 001 — Prompt Engine Protocol Enforcement
* **Date Adopted**: 2026-07-28
* **Observation**: AI coding agents default to dumping large amounts of code and finishing projects in one turn.
* **Problem**: Students receive finished code without learning underlying concepts or trade-offs.
* **Decision**: Implement a multi-section system prompt (`src/scaffold/prompt.py`) enforcing 5 explicit protocol rules.
* **Rationale**: Markdown structure with explicit rule numbering forces model compliance.

---

### Entry 002 — Adaptive Complexity-Aware Milestone Generation
* **Date Adopted**: 2026-07-28
* **Observation**: Fixed 4-milestone roadmaps were too long for simple scripts and too brief for full-stack apps.
* **Problem**: Inflexible roadmap sizing caused friction across different project types.
* **Decision**: Update `src/scaffold/generator.py` with dynamic scaling rules (2–3 for simple, 4–5 for moderate, 6–10 for complex).
* **Rationale**: LLM analyzes project description scope first and scales milestone count automatically.

---

### Entry 003 — Local `.scaffold/session.json` State Persistence
* **Date Adopted**: 2026-07-28
* **Observation**: Students need session persistence across terminal restarts.
* **Problem**: Cloud database requirements add friction and privacy concerns for student code.
* **Decision**: Implement `.scaffold/session.json` local file storage in `src/scaffold/session.py`.
* **Rationale**: Zero external server dependency, simple JSON serialization, project-scoped isolation.

---

### Entry 004 — Decoupled Reflection Analytics & Learning Timeline
* **Date Adopted**: 2026-07-28
* **Observation**: Student learning metrics and concept histories need tracking.
* **Problem**: Storing detailed analytics inside `session.json` bloats session state and risks data corruption.
* **Decision**: Create separate `analytics.py` (`.scaffold/analytics.json`) and `timeline.py` (`.scaffold/timeline.json`).
* **Rationale**: Clean separation of concerns; enables future dashboard reporting without touching active session state.
