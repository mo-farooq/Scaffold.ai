# 🏗️ Scaffold.ai — Learn to Code with AI

[![skills.sh](https://img.shields.io/badge/skills.sh-scaffold-blue?style=for-the-badge&logo=anthropic)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Target Agent Ecosystem](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Claude%20Code%20%7C%20Cursor%20%7C%20Codex-6c5ce7?style=for-the-badge)](https://github.com/mo-farooq/Scaffold.ai)

> Build real software with AI while becoming capable of explaining every important decision.

Scaffold.ai is the anti-vibe-coding Socratic mentor for anyone learning to code or building
software with modern AI agents. Instead of letting the agent write all the code—robbing you
of deep understanding and problem-solving skills—Scaffold turns your agent into an active learning
partner: the agent handles repetitive project glue and boilerplate, while you own the core
algorithms, trade-offs, and explanations.

Whether you are learning a new language, building your first fullstack app, or exploring low-level
systems, Scaffold ensures you stay in the driver's seat and master how to code.

## ⚡ Start in Five Minutes

Install the skill into your project with the universal skills CLI:

```bash
npx skills add mo-farooq/scaffold
```

Then tell your agent what you want to learn or build:

```text
/scaffold "I want to learn Go by building a CLI task manager"
```

*(Or simply ask `/scaffold` and let your agent help you design a learning project tailored to your level.)*

Scaffold will:

1. Initialize a `PROGRESS.md` learning dashboard tailored to your goal.
2. Decompose the project into sequential, bite-sized milestones.
3. Separate agent-owned setup from learner-owned core logic.
4. Create explicit `TODO(scaffold)` stubs in Mentor Mode.
5. Give you one small next action and a Level 1 progressive hint path.

## 💡 Learn Any Language or Stack

Scaffold is language-agnostic. Bring whatever you want to learn:

| Language / Goal | Example Scaffold Prompt | What You Own |
| :--- | :--- | :--- |
| **Go** | `/scaffold "Learn Go concurrency with a worker pool"` | Mutex locks, channels, and worker dispatching |
| **Python** | `/scaffold "Build an async task queue in Python"` | Task serialization, retry loops, and event loops |
| **TypeScript** | `/scaffold "Learn state management with an event ledger"` | In-memory event reducer and state validation |
| **Rust** | `/scaffold "Learn Rust ownership with a mini key-value store"` | Hash map indexing, buffer parsing, and file sync |

Scaffold configures the project harness, test runners, and entry points, then hands you the keyboard with focused `TODO(scaffold)` blocks and a progressive hint system when you get stuck.

## 🧭 What a Session Feels Like

The agent starts with the active milestone—not a passive code dump:

```text
Architectural goal: parse and persist structured tasks with validation.
You own: the core state transition and serialization logic inside TODO(scaffold).
I own: CLI argument parsing, environment setup, and the test harness.
Your next action: implement the task validation state machine.
Need help? Ask for a Level 1 analogy and guiding question.
```

Keep `PROGRESS.md` open beside your code. It shows the current objective, next action,
milestone state, architecture decisions, and Aha Moments.

## 🎛️ Two Learning Modes

### Mentor Mode (default)

The agent writes environment setup, configuration, entry points, test harnesses, and file
skeletons. Core algorithmic work remains behind explicit `TODO(scaffold)` markers for the
learner to implement.

### Hardcore Mode

The learner writes all source files, boilerplate, and algorithms. The agent provides
architecture, questions, and progressive hints, but writes no source-code files. Progress
metadata may still be generated.

## 🔄 The Learning Loop

### 1. Build

Work only on the active milestone. The agent explains the architectural goal, inputs and
outputs, constraints, ownership boundary, and first action.

### 2. Get unstuck

Ask for help without receiving a solution dump:

1. **Level 1:** analogy and guiding question
2. **Level 2:** control flow or language-agnostic pseudocode
3. **Level 3:** API direction and edge-case pointers

Level 2 and Level 3 guidance is recorded as Guided at the reflection gate.

### 3. Defend

When the milestone is complete, ask for `/scaffold verify`. The agent reviews the relevant
diff across correctness, edge cases, complexity, and security/resource safety, then asks one
architectural trade-off question.

Only after you explain the design in your own words does the agent run the deterministic
recorder that updates `PROGRESS.md`.

### 4. Reflect

Each gate records a one-sentence Aha Moment. After the final milestone, the agent summarizes
what you built, which concepts you demonstrated, which milestones needed guidance, and what
to build next.

## ⚡ Everyday Mode: `/scaffold quiz`

Use Scaffold on production work too:

```text
/scaffold quiz
```

The agent inspects your staged and unstaged diff and asks:

1. What core problem does this change solve?
2. What is the execution flow of the primary change?
3. Under what runtime scenario could it fail or perform poorly?

## 🧱 What Is Guaranteed

The deterministic scripts guarantee:

- Safe initialization unless `--force` is explicitly requested
- Sequential milestone progression
- Idempotent progress updates
- Progress bars, mastery states, Aha Moments, and completion badges

The guardrails and Socratic behavior are model-dependent instructions. They are not an
operating-system sandbox, so Scaffold describes that boundary honestly.

## 🗺️ Curated Practice Playgrounds

Looking for ready-made challenges? Scaffold includes curated systems playgrounds that guide
you through building foundational systems from raw primitives:

```text
/scaffold track redis
```

| Playground | What You Build | Core Concepts |
| :--- | :--- | :--- |
| [⚡ Redis Clone](skills/scaffold/assets/tracks/redis-from-scratch.md) | In-memory database speaking RESP | TCP, parsing, state, TTL, AOF |
| [🌳 Git from Scratch](skills/scaffold/assets/tracks/git-from-scratch.md) | Content-addressable version control | Hashes, zlib, Merkle trees, commit DAGs |
| [🌐 HTTP/1.1 Server](skills/scaffold/assets/tracks/http-server-from-scratch.md) | Server from raw TCP sockets | Framing, headers, routing, keep-alive |
| [🗄️ Mini SQLite](skills/scaffold/assets/tracks/sqlite-from-scratch.md) | Embedded relational database | Pages, serialization, B-trees, SQL |
| [🐳 Container Runtime](skills/scaffold/assets/tracks/docker-from-scratch.md) | Lightweight process isolation runtime | Namespaces, cgroups, OverlayFS |

## 🔌 Compatibility

Scaffold is distributed as one canonical `skills/scaffold/` skill package. See the
[compatibility matrix](docs/compatibility.md) for installation surfaces and validation
status. A surface is not labeled fully supported until its first-session workflow has been
manually validated.

## 📚 Project Resources

- [Skill instructions](skills/scaffold/SKILL.md)
- [Socratic hinting and reflection rubric](skills/scaffold/references/socratic-rubric.md)
- [Architectural trade-off prompts](skills/scaffold/references/tradeoff-prompts.md)
- [Guardrail behavior](skills/scaffold/assets/rules/scaffold-guardrails.md)
- [Architecture decision record](docs/adr/ADR-008-antigravity-skills-architecture.md)

## 📦 Legacy Standalone CLI Harness

The original Python/Textual terminal harness is preserved in the
[`archive/cli-harness`](https://github.com/mo-farooq/Scaffold.ai/tree/archive/cli-harness)
branch and release tag [`v0.1.0-harness`](https://github.com/mo-farooq/Scaffold.ai/releases/tag/v0.1.0-harness).

## 📄 License

MIT © [Mohammad Farooq](https://github.com/mo-farooq)
