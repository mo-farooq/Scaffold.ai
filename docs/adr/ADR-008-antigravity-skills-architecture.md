# ADR-008: Antigravity Native Skill & Universal `skills.sh` Distribution Architecture

* **Status**: Accepted
* **Date**: 2026-11-05
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

Scaffold.ai initially developed a standalone Python harness and Textual TUI (`scaffold`). However, modern developers increasingly use in-editor agentic coding environments—specifically **Google Antigravity**, **Claude Code**, **Cursor**, **Codex**, and **OpenCode**.

In these environments, students suffer from **"vibe coding" and "AI skill atrophy"**: agents aggressively write complete solutions, depriving learners of conceptual mastery and system design experience.

To achieve maximum adoption and virality (targeting 1,000+ GitHub stars), Scaffold must be installable via a single universal command (`npx skills add mo-farooq/scaffold` or native Antigravity skills) and run natively inside the IDE, providing an anti-vibe-coding Socratic mentor directly where developers code.

---

## 2. Decision Drivers

* **Zero-Friction Universal Installation**: One command installable via `npx skills add` across Antigravity, Claude Code, Cursor, and Codex.
* **Dual-Layer In-IDE Pattern**:
  * Continuous behavioral enforcement (blocking solution dumps via an always-on Rule).
  * On-demand procedural guidance (milestone generation and reflection gating via a Progressive Skill).
* **Native Split-Pane Experience**: The developer codes on the left pane while a live `PROGRESS.md` renders in the right split preview pane.
* **Viral Open-Source Momentum**: "Build X from scratch" curriculum tracks, shareable mastery badges, and a clear anti-vibe-coding narrative to drive Hacker News / Reddit virality.
* **Deterministic Execution & Low Token Overhead**: Keep core instructions compact (<5,000 tokens) by offloading initialization, checklist toggling, and score calculations to standalone scripts (`.mjs`).

---

## 3. Considered Options

* **Option 1: Python CLI Only**: Keep Scaffold strictly as a standalone terminal application.
  * *Drawbacks*: Requires students to leave their primary editor or switch windows. Limits distribution to Python users and misses the trending agent skills ecosystem.
* **Option 2: VS Code / Antigravity Native Extension Only**: Build a heavyweight TypeScript extension.
  * *Drawbacks*: High maintenance, editor-specific, cannot be shared with Claude Code or Cursor.
* **Option 3: The Dual-Layer Native Skill Pattern (`skills/` + `rules/`) with `skills.sh` Compatibility (Chosen)**:
  * Package Scaffold into standard Antigravity & `skills.sh` layout.
  * Pair an always-on guardrail rule (`rules/scaffold-guardrails.md`) with a progressive-disclosure skill (`skills/scaffold/SKILL.md`), deterministic scripts (`scripts/init-scaffold.mjs`, `scripts/verify-gate.mjs`), reference rubrics, and pre-built viral tracks.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3**.

### Architecture:

```
scaffold/
├── package.json                      # npm / skills.sh package metadata
├── rules/
│   └── scaffold-guardrails.md        # Antigravity always-on rule banning direct solution dumps
├── skills/
│   └── scaffold/
│       ├── SKILL.md                  # Core manifest + Socratic state machine (<5,000 tokens)
│       ├── scripts/
│       │   ├── init-scaffold.mjs     # Creates PROGRESS.md & sets up workspace guardrails
│       │   └── verify-gate.mjs       # Validates milestone completion & updates mastery stats
│       ├── references/
│       │   ├── socratic-rubric.md    # Multi-level hinting without spoiling answers
│       │   └── tradeoff-prompts.md   # Architectural trade-off reflection questions
│       └── assets/
│           └── PROGRESS.template.md  # Live checklist & comprehension tracker template
├── tracks/                           # Pre-built curriculum tracks
│   ├── redis-from-scratch.md
│   ├── git-from-scratch.md
│   ├── http-server-from-scratch.md
│   ├── sqlite-from-scratch.md
│   └── docker-from-scratch.md
└── README.md                         # Anti-vibe-coding pitch & split-screen demo
```

---

## 5. Heritage & Archive

The prior standalone CLI / TUI prototype is archived in branch `archive/cli-harness` and tag `v0.1.0-harness`.
