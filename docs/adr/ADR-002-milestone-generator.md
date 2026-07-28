# ADR-002: Dynamic Milestone Generator with Adaptive Complexity Scaling

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

Hardcoding milestones for every possible student project idea is unmaintainable. The tool needed a way to dynamically decompose any project description (from micro-scripts to full-stack platforms) into a structured learning roadmap.

---

## 2. Decision Drivers

* **Adaptive Scaling**: Simple scripts need 2–3 milestones; complex full-stack apps need 6–10.
* **Guaranteed JSON Structure**: LLM must output clean, parseable JSON arrays without extra text.
* **Low Latency & Reliability**: Fast generation via `gemini-3.1-flash-lite`.

---

## 3. Decision Outcome

**Chosen Option**: `google-genai` SDK with `response_mime_type="application/json"` and `response_schema=list[str]`. Implemented `generate_milestones()` in `src/scaffold/generator.py`.

### Positive Consequences
* Schema enforcement guarantees structured array returns.
* Adaptive scaling dynamically produces 2 to 10 milestones based on project scope.
* `_clean_json_text()` sanitizes markdown fences if returned.

---

## 4. Future Revisit Criteria

* Revisit when adding user customization of milestone granularity (e.g. `--depth detailed`).
