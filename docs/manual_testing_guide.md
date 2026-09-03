# Scaffold.ai — Comprehensive Manual Testing Guide

This guide provides a structured, step-by-step manual testing playbook for **Scaffold.ai**. Whether you are testing new features, verifying bug fixes, or demonstrating capabilities, follow these recipes to thoroughly test every component.

---

## 🎛️ Option 1: The Interactive Developer Test Lab (Recommended)

The easiest way to test everything is via the **Interactive Developer Test Lab** — an all-in-one terminal harness that lets you test any component with a single keystroke:

```bash
uv run python scripts/test_lab.py
```

### Main Menu Options:
```
======================================================================
           🔬 SCAFFOLD.AI — DEVELOPER TEST LAB & PLAYGROUND
======================================================================
  [1] 🎯 Test Dynamic Milestone Generator (Preset or Custom Idea)
  [2] 📜 Test Learning Mode Prompt Engine (Inspect Rendered System Prompt)
  [3] 🔄 Test Session State Machine (Init, Advance, Reset, Inspect JSON)
  [4] 🧠 Test Reflection Evaluator (Evaluate Good vs Weak Answers Live)
  [5] 🔌 Test Agent Adapters (Send Test Message to Gemini or Claude CLI)
  [6] 🛡️  Test Prompt Protocol Validator (Score Responses Against 6 Rules)
  [7] 📊 Inspect Analytics & Learning Timeline (.scaffold/ Records)
  [8] 🚀 Launch Interactive TUI Application (Full Terminal Experience)
  [9] 🧪 Run All Automated Quality Gates (verify.sh + e2e_verify.py)
  [0] ❌ Exit Test Lab
======================================================================
```

---

## 🖥️ Option 2: Testing the Standalone Terminal Application (TUI)

The primary user interface is the interactive Textual terminal app.

### How to Launch:
```bash
# Using uv:
uv run scaffold

# Or as a Python module:
uv run python -m scaffold.tui
```

### Test Scenario A: New Project Onboarding Flow
1. **Welcome Screen**:
   - Verify the branded banner renders cleanly.
   - Select `[🆕 Start New Project]`.
2. **Setup Screen**:
   - In the input field, type:
     ```text
     A command-line weather application in Python using OpenWeather API
     ```
   - Press **Enter**.
   - **Verify**: A loading message appears ("*Generating milestones...*").
   - **Verify**: Within 3–6 seconds, a markdown-formatted milestone list appears (typically 3–4 milestones).
   - Click `[🚀 Start Learning]`.
3. **Session Screen**:
   - **Verify**: The screen splits into a Left Chat Panel (75%) and Right Milestone Sidebar (25%).
   - **Verify**: The chat log displays a welcome message showing the current milestone highlighted.
   - **Verify**: The right sidebar shows Milestone 1 marked with `🔵 1. ... ◄` and remaining milestones marked `⬜`.

---

### Test Scenario B: Active Conversation & AI Response Flow
1. In the bottom input bar of the session screen, type:
   ```text
   What should we build first for milestone 1?
   ```
2. Press **Enter**.
3. **Verify**:
   - Your message appears labeled `👤 You: ...`.
   - A `⏳ Thinking...` indicator appears.
   - Within 2–4 seconds, the AI Tutor's response streams in.
   - **Check Protocol Compliance**:
     - Explains the goal first.
     - Stays strictly in scope of Milestone 1.
     - Explains trade-offs (e.g. why dataclass over dict).
     - Ends with a reflective question (`🤔 Reflective Question: ...`).
   - The session state transitions to `AWAITING_REFLECTION`.

---

### Test Scenario C: Reflection Evaluation Flow (Retry vs Advance)
1. **Test Weak / Confused Answer**:
   - Type:
     ```text
     Because dataclasses make the code run 10x faster than dictionaries.
     ```
   - Press **Enter**.
   - **Verify**:
     - Evaluator marks it as `🔄 RETRY` with a low score (~20-40%).
     - Feedback explains that dataclasses are for type safety and structure, not speed.
     - A targeted **Hint** is provided without revealing direct code.
     - Milestone does **not** advance.
2. **Test Strong / Thoughtful Answer**:
   - Type:
     ```text
     Dataclasses provide formal type hints and attribute validation, which prevents runtime key errors that can happen with dictionaries.
     ```
   - Press **Enter**.
   - **Verify**:
     - Evaluator marks it as `✅ PASSED` with a high score (~85-95%).
     - Encouraging feedback confirms understanding.
     - The milestone advances: Milestone 1 turns `✅`, Milestone 2 turns `🔵 2. ... ◄`.
     - Sidebar stats update (pass rate and attempt counts).

---

### Test Scenario D: Dashboard, Timeline & Resume Flow
1. Press `Ctrl+S` to open the **Status Dashboard**.
   - **Verify**: Milestone progress bar, pass rate %, total time, and learning timeline entries are visible.
   - Click `[← Back]` to return to the session.
2. Press `Ctrl+Q` to exit the app.
3. Relaunch: `uv run scaffold`.
   - **Verify**: `[📂 Resume Existing Project]` is now enabled.
   - Click Resume and verify your previous session is restored seamlessly.

---

## 🔍 Option 3: Individual Engine Preview Scripts

You can also test each underlying engine in isolation using the standalone preview scripts in the root directory:

### 1. Test Dynamic Milestone Generator
```bash
# Simple script idea (should generate 2-3 milestones):
uv run python preview_generator.py "A simple Python script to calculate word frequencies in a text file"

# Complex full-stack idea (should generate 5-8 milestones):
uv run python preview_generator.py "A full-stack e-commerce marketplace with FastAPI, Stripe payments, PostgreSQL, and React frontend"
```
**Expected**: Clean JSON output listing milestones; counts automatically scale with complexity.

---

### 2. Test Prompt Engine Harness
```bash
# Preview Milestone 1 system prompt:
uv run python preview_prompt.py --milestone 1

# Preview Milestone 3 system prompt (shows completed milestones in context):
uv run python preview_prompt.py --milestone 3
```
**Expected**: Multi-section markdown prompt containing Role, Project Overview, Current Milestone, Completed Milestones, and all 5 Learning Mode Rules.

---

### 3. Test Session State Machine
```bash
uv run python preview_session.py
```
**Expected**: Demonstrates initialization, local persistence to `.scaffold/session.json`, milestone advance, progress percentage calculation, and reset.

---

### 4. Test Reflection Evaluator
```bash
uv run python preview_evaluator.py
```
**Expected**: Live evaluation of two sample answers against Gemini API — strong answer receives `PASSED` (`ADVANCE`), confused answer receives `RETRY` with a helpful hint.

---

### 5. Test Agent Adapters
```bash
# Test Gemini API Adapter:
uv run python preview_adapters.py --adapter gemini --message "How should I structure the data model?"

# Test Claude Code CLI Adapter (if claude is installed in PATH):
uv run python preview_adapters.py --adapter claude --message "Explain dataclasses"
```
**Expected**: Agent response received with latency metrics and full protocol formatting.

---

## ⚠️ Edge Cases, Failure Recovery & Stress Tests

| Test Scenario | How to Trigger | Expected Behavior |
|---|---|---|
| **Missing API Key** | `GEMINI_API_KEY="" uv run scaffold` | Gracefully notifies user with actionable instructions to set `GEMINI_API_KEY`. No crash. |
| **Empty User Message** | Press Enter in input bar without typing | Input is safely ignored; no empty network calls triggered. |
| **Corrupted Session File** | Corrupt `.scaffold/session.json` with invalid JSON | App detects corruption, alerts user, and offers fresh project initialization. |
| **Multiple Retries** | Submit 3 failed reflection answers in a row | System tracks every attempt in `.scaffold/analytics.json`, updates pass rate, and offers evolving hints. |
| **Project Reset** | Call `reset_session()` or delete `.scaffold/` | State resets cleanly; Resume button disables on next launch. |

---

## 🛡️ Automated Quality Gates Quick Reference

Before submitting any code changes, always verify all gates pass:

```bash
# Run all quality gates in one command:
./scripts/verify.sh

# Run full-stack headless simulation:
uv run python scripts/e2e_verify.py

# Run performance benchmarks:
uv run python scripts/benchmark.py
```
