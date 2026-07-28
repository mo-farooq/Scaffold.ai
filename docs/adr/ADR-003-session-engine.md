# ADR-003: Session State Machine & `.scaffold/session.json` Storage

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

Students need their learning progress preserved across terminal restarts and computer reboots. Progress must be stored locally in the student's project directory without requiring remote servers or cloud accounts.

---

## 2. Decision Outcome

**Chosen Option**: Local `.scaffold/session.json` storage managed by `src/scaffold/session.py`.

### Positive Consequences
* `SessionState` enum (`IN_PROGRESS`, `AWAITING_REFLECTION`, `COMPLETED`) provides explicit state transitions.
* `get_current_context(session)` bridges session state directly into prompt engine inputs.
* Zero external database dependencies; human-readable JSON format.
