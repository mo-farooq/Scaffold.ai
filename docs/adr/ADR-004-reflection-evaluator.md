# ADR-004: Student Reflection Evaluator & Pedagogical Grading

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

To unlock the next milestone, students answer a reflective question. We needed a grading engine that evaluates conceptual comprehension rather than verbatim string matching.

---

## 2. Decision Outcome

**Chosen Option**: `src/scaffold/evaluator.py` using `gemini-3.1-flash-lite` with structured `EvaluationResult` output (`passed: bool`, `score: float`, `feedback: str`, `hint: str | None`, `suggested_action: str`).

### Positive Consequences
* Evaluates trade-off awareness and reasoning principles.
* Generates constructive hints when `passed == False` without spoiling code.
