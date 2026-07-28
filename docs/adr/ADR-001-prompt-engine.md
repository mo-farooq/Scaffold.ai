# ADR-001: Learning Mode System Prompt Engine & Protocol Rules

* **Status**: Accepted
* **Date**: 2026-07-28
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

AI coding assistants (e.g. Claude Code, Cursor, Copilot) are optimized for raw task completion velocity, dumping large blocks of code and completing entire projects in a single turn. For student developers, this leads to passive consumption without conceptual understanding. We needed a harness prompt that forces the AI into a patient teaching role.

---

## 2. Decision Drivers

* **Pedagogical Alignment**: Pacing development around student comprehension.
* **Deterministic Scope Enforcer**: Preventing the AI from jumping ahead to future milestones.
* **Reflective Anchor**: Requiring a student reflection question before stopping.

---

## 3. Considered Options

* **Option 1**: Loose system prompt with high-level instruction ("Be a tutor").
* **Option 2**: Structured multi-section markdown prompt enforcing 5 explicit protocol rules (`scaffold.prompt`).
* **Option 3**: Hardcoded fine-tuned model checkpoint.

---

## 4. Decision Outcome

**Chosen Option**: **Option 2**. Implemented `MilestoneContext` and `build_prompt()` in `src/scaffold/prompt.py`.

### Positive Consequences
* Markdown structure (`# Title`, `## Role`, `## Milestone`, `## Protocol`) is easy for LLMs to follow.
* Completed milestone history is explicitly injected (`The student has already completed: ...`).
* Enforces single-milestone focus, step-by-step code blocks, trade-off explanations, and `### 🤔 Reflective Question`.

### Negative Consequences / Trade-offs
* Consumes ~500 tokens of context per request for prompt instructions.

---

## 5. Future Revisit Criteria

* Revisit when supporting multi-agent collaboration or interactive agent tool calls.
