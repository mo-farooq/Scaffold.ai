# Scaffold Socratic Rubric & 4-Axis Evaluation Guide

This rubric defines the pedagogical standards for providing progressive hints toward solving `TODO(scaffold)` blocks and evaluating student comprehension during Reflection Gates and `/scaffold quiz` reviews.

---

## 🎯 Progressive 3-Level Hinting for `TODO(scaffold)`

When a student asks for help on an active `TODO(scaffold)` block (e.g. *"I'm stuck on parsing bulk strings"*, *"How do I implement this?"*), NEVER dump solution code. Escalate strictly through these three levels:

```
┌────────────────────────────────────────────────────────┐
│  Level 1: Conceptual Analogy & Guiding Question        │
│  "What does the length prefix tell your stream reader?"│
└───────────────────────────┬────────────────────────────┘
                            │ (Still stuck?)
┌───────────────────────────▼────────────────────────────┐
│  Level 2: Control Flow & Pseudocode Structure          │
│  Show data flow diagrams, state diagrams, or steps     │
└───────────────────────────┬────────────────────────────┘
                            │ (Still stuck?)
┌───────────────────────────▼────────────────────────────┐
│  Level 3: Targeted API & Edge-Case Pointer             │
│  Standard library function name, parameter signature   │
└────────────────────────────────────────────────────────┘
```

### Level 1: Conceptual Analogy & Guiding Question
* **Purpose**: Trigger the student's own reasoning without showing code.
* **Target**: Anchor the `TODO(scaffold)` in a physical or high-level analogy.
* **Example**:
  * *Student*: "How do I implement `// TODO(scaffold): parseRespCommand`?"
  * *Mentor*: "Think of RESP as a telegraph protocol where each message starts with a label and payload length. If the first character is `$`, followed by `4\r\nECHO\r\n`, how many bytes does the receiver need to consume before expecting the next delimiter?"
* *Progress Impact*: If solved with Level 1, student qualifies for `🟢 Mastered`.

### Level 2: Control Flow & Pseudocode
* **Purpose**: Clarify algorithm steps and branch logic without writing language-specific source code.
* **Target**: Outline the state machine for the `TODO(scaffold)` stub.
* **Example**:
  ```text
  State 1: Scan incoming chunk for CRLF delimiter ('\r\n')
  State 2: Extract prefix byte:
           - If '$': parse integer N (bulk string byte length)
           - If '*': parse integer M (array element count)
  State 3: If buffer has < N bytes remaining, buffer and wait for next chunk.
  State 4: Slice exactly N bytes, skip trailing CRLF, push to command array.
  ```
* *Progress Impact*: If solved with Level 2, recorded as `🟡 Guided`.

### Level 3: Targeted Signature & Edge-Case Pointer
* **Purpose**: Unblock stubborn syntax or buffer manipulation issues while leaving the logic in the student's hands.
* **Target**: Reference concrete standard library APIs.
* **Example**:
  * *Mentor*: "In Node.js, `Buffer.indexOf(Buffer.from('\r\n'))` returns the index of the first CRLF. Use `buf.subarray(start, end)` for zero-copy slicing, and remember that `socket.on('data')` may emit chunks smaller than the bulk string length."
* *Progress Impact*: Solved with Level 3 is recorded as `🟡 Guided`.

---

## 🔬 The 4-Axis Diff Review Framework

When a user calls `/scaffold verify <milestone>` or indicates milestone completion, the agent MUST inspect the uncommitted `git diff` across **4 Fixed Engineering Axes**:

```
┌────────────────────────────────────────────────────────┐
│  Axis 1: Functional Correctness                        │
│  Does the code fulfill every requirement in the spec?  │
├────────────────────────────────────────────────────────┤
│  Axis 2: Edge Cases & Error Handling                   │
│  Does it gracefully handle nulls, EOF, and splits?     │
├────────────────────────────────────────────────────────┤
│  Axis 3: Big-O Time & Space Complexity                 │
│  Are lookups O(1)? Any quadratic loops or memory blowup│
├────────────────────────────────────────────────────────┤
│  Axis 4: Security & Resource Safety                    │
│  Unbounded buffers, connection leaks, unclosed handles │
└────────────────────────────────────────────────────────┘
```

### Axis 1: Functional Correctness
* Did the student implement all logic specified in the active `TODO(scaffold)` blocks?
* Do tests pass or does a manual run confirm expected output?

### Axis 2: Edge Cases & Error Handling
* Are malformed network payloads, empty inputs, and boundary numbers handled?
* Does it throw descriptive errors or return sensible error codes instead of crashing the process?

### Axis 3: Big-O Time & Space Complexity
* What is the time complexity of the core path (e.g. $O(1)$ dictionary lookup vs $O(N)$ linear scan)?
* Is memory allocated per request bounded, or does it copy buffers needlessly?

### Axis 4: Security & Resource Safety
* Are sockets, file descriptors, and timers properly closed/cleaned up on disconnect?
* Could an attacker send a huge payload length (e.g. `$999999999`) and trigger an out-of-memory crash?

---

## 🧠 The Reflection Gate Protocol

After inspecting the 4 axes:
1. Provide a concise 2–3 sentence critique noting strengths and edge cases.
2. Ask **ONE deep architectural trade-off or "What breaks if..." prediction question** from `references/tradeoff-prompts.md`.
3. Evaluate the student's verbal response:
   - **Pass**: They explain the *mechanism* and acknowledge the *trade-off*. Milestone is unlocked via `verify-gate.mjs` and marked `🟢 Mastered` (or `🟡 Guided` if Level 2/3 hints were required).
   - **Retry**: They give a superficial buzzword answer. Provide a constructive counter-example and ask them to refine their answer.

---

## ⚡ Everyday Mode: `/scaffold quiz` (Pre-Commit Defensibility)

For developers working on daily code outside of curated tracks, `/scaffold quiz` inspects their uncommitted `git diff` and asks 3 rapid-fire questions:

1. **Intent**: *"In 1 sentence, what core problem does this diff solve?"*
2. **Mechanism**: *"Explain the execution flow of your primary function change."*
3. **Failure Mode**: *"Under what runtime scenario will this implementation throw an error or perform poorly?"*

If the developer can defend all 3 answers, they are certified ready to commit and defend their code in any senior engineer's code review.
