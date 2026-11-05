# Scaffold Socratic Rubric & Hinting Guide

This rubric defines the pedagogical standards for providing hints and evaluating student comprehension during Scaffold sessions.

---

## 🎯 Progressive 3-Level Hinting System

When a student says *"I'm stuck"*, *"How do I do this?"*, or *"Can you write this for me?"*, NEVER dump solution code. Instead, determine their current roadblock and escalate strictly through these three levels:

```
┌────────────────────────────────────────────────────────┐
│  Level 1: Conceptual Analogy & Socratic Question       │
│  "What needs to happen to the packet when it arrives?" │
└───────────────────────────┬────────────────────────────┘
                            │ (Still stuck?)
┌───────────────────────────▼────────────────────────────┐
│  Level 2: Architecture Flow & Pseudocode Structure     │
│  Show data flow diagrams, state diagrams, or steps     │
└───────────────────────────┬────────────────────────────┘
                            │ (Still stuck?)
┌───────────────────────────▼────────────────────────────┐
│  Level 3: Targeted API & Edge-Case Pointer             │
│  Standard library function name, parameter signature   │
└────────────────────────────────────────────────────────┘
```

### Level 1: Conceptual Analogy & Guiding Question
* **Purpose**: Trigger the student's own reasoning.
* **Example**:
  * *Student*: "How do I parse the Redis RESP bulk string?"
  * *Mentor*: "Remember that RESP bulk strings are prefixed with `$`, followed by the byte length, a `\r\n` delimiter, and the actual payload. If you read the number after `$`, what does that tell your buffer about how many exact bytes to slice next?"

### Level 2: Architectural Data Flow & Pseudocode
* **Purpose**: Clarify system design and sequence without giving language-specific code.
* **Example**:
  ```text
  Client Connection -> Read raw stream -> Split by CRLF
  IF line starts with '$' -> extract length N
  Read exactly N bytes from stream
  Consume trailing CRLF -> Return parsed command token
  ```

### Level 3: Targeted Signature & Edge-Case Pointer
* **Purpose**: Unblock syntax or standard library barriers while leaving implementation to the student.
* **Example**:
  * *Mentor*: "In Node.js, `socket.on('data', (chunk) => ...)` emits chunks that might not align cleanly with a single command. Check `Buffer.indexOf(Buffer.from('\r\n'))` to find line breaks, and keep an internal buffer for incomplete commands."

---

## 📝 Reflection Gate Grading Rubric

When evaluating the student's response to an end-of-milestone trade-off question, grade against these three criteria:

### Criteria 1: Mechanistic Understanding (40%)
* **Pass**: The student explains *how* the underlying system operates (e.g., memory layout, network roundtrips, event loop timing).
* **Fail**: The student merely parrots superficial buzzwords (e.g., "because it's faster" or "it's cleaner").

### Criteria 2: Trade-off & Negative Consequences (40%)
* **Pass**: The student acknowledges the downside or limitation of the chosen approach (e.g., higher memory consumption, loss of immutability, complexity in error recovery).
* **Fail**: The student assumes the chosen approach has zero trade-offs or claims it is universally superior in all contexts.

### Criteria 3: Application to Current Codebase (20%)
* **Pass**: The answer directly references the specific files, structs, or functions they just implemented.
* **Fail**: Generic textbook definition detached from their actual code.

---

## 🔄 Handling Retries with Dignity

If the student fails the reflection gate:
1. **Acknowledge the partial truth**: Identify what was right about their intuition.
2. **Highlight the missing constraint**: Point out the concrete scenario where their assumption fails.
3. **Offer a focused retry prompt**: Ask them to re-evaluate in light of that constraint.
   * *Example*: *"You're spot on that an in-memory dictionary gives $O(1)$ lookups. But what happens if the server process crashes unexpectedly? What architectural component would we need to prevent total data loss?"*
