# ADR-005: Quality Gates, Prompt Validation & Reflection Analytics

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

To reach production quality, Scaffold.ai requires automated quality verification (`ruff`, `mypy`, `pytest`), programmatic validation of agent prompt protocol outputs, and decoupled analytics tracking for student learning metrics.

---

## 2. Decision Outcome

**Chosen Option**:
* Single verification entrypoint: `scripts/verify.sh`.
* Decoupled analytics store: `.scaffold/analytics.json` via `src/scaffold/analytics.py`.
* Programmatic protocol validator: `src/scaffold/validator.py`.

### Positive Consequences
* Ensures 100% type safety, code formatting, and test health before commits.
* Keeps analytics separate from session state for reporting and diagnostic analysis.
