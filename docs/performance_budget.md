# Scaffold.ai — Performance Budget Specifications

This document defines performance thresholds and latency budgets for Scaffold.ai.

---

## Performance Targets

| Operation | Metric | Target Budget | Maximum Threshold |
|---|---|---|---|
| **System Prompt Generation** (`build_prompt`) | Latency | < 5 ms | < 20 ms |
| **Session Operations** (`load_session`, `save_session`) | Latency | < 10 ms | < 50 ms |
| **Milestone Generation** (`generate_milestones`) | LLM Latency | < 3.0 s | < 8.0 s |
| **Reflection Evaluation** (`evaluate_answer`) | LLM Latency | < 2.5 s | < 6.0 s |
| **Prompt Protocol Validation** (`validate_protocol`) | Latency | < 15 ms | < 50 ms |
| **Test Suite Execution** (`pytest`) | Total Time | < 5.0 s | < 15.0 s |

---

## Measuring Performance

Run the benchmark script:
```bash
uv run python scripts/benchmark.py
```
