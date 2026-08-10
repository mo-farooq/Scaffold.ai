# ADR-006: Agent Adapter Layer & Multi-Agent Connector Architecture

* **Status**: Accepted
* **Date**: 2026-08-09
* **Deciders**: Scaffold.ai Core Team

---

## 1. Context and Problem Statement

Student developers use different AI coding agents — some use Anthropic's Claude Code CLI (`claude`), while others use direct Gemini API calls or future open-source agent CLIs. Scaffold.ai needs a provider-agnostic adapter layer to inject the Learning Mode system prompt into any target agent without coupling domain logic to a specific vendor API or CLI syntax.

---

## 2. Decision Drivers

* **Provider Agnosticism**: Unified interface (`AgentAdapter`) supporting both CLI subprocess wrappers and direct API SDK clients.
* **System Prompt Injection**: Ability to pass custom system instructions (`system_instruction` / system prompt flags).
* **Extensibility**: Easy plug-and-play architecture for adding new agents in the future.

---

## 3. Considered Options

* **Option 1**: Direct coupling to Gemini API only.
* **Option 2**: Abstract Base Class (`AgentAdapter`) with concrete subclasses (`ClaudeAdapter`, `GeminiAdapter`) and a factory registry (`get_adapter()`).
* **Option 3**: External proxy server routing HTTP requests to agent endpoints.

---

## 4. Decision Outcome

**Chosen Option**: **Option 2**. Implemented `src/scaffold/adapters/base.py`, `gemini.py`, `claude.py`, and `__init__.py`.

### Positive Consequences
* `AgentAdapter.send_message(prompt: str, system_prompt: str) -> AgentResponse` provides a single, uniform interface.
* Subprocess execution for `claude` CLI captures stdout/stderr cleanly while supporting stdin piping.
* Direct Gemini API client provides high-speed structured responses.

---

## 5. Future Revisit Criteria

* Revisit when supporting streaming responses (server-sent events / real-time terminal output streaming).
