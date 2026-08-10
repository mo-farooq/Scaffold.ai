"""Agent Adapter Base Class for Scaffold.ai.

Defines the abstract interface that all AI agent adapters must implement,
along with the AgentResponse dataclass for uniform response handling.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    """Uniform response object returned by all agent adapters.

    Attributes
    ----------
    content:
        The text content of the agent's response.
    model_name:
        The model or CLI binary that produced the response.
    latency_seconds:
        Wall-clock time in seconds for the agent call.
    raw_response:
        The raw, unprocessed response object from the underlying SDK or subprocess.
    metadata:
        Optional key-value metadata (e.g. token counts, finish reasons).
    """

    content: str
    model_name: str = ""
    latency_seconds: float = 0.0
    raw_response: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentAdapter(ABC):
    """Abstract base class for AI agent adapters.

    Every adapter must implement `send_message()`, which accepts a user message
    and an optional system prompt, and returns an `AgentResponse`.

    Subclasses may wrap direct SDK clients (e.g. Gemini API) or external CLI
    binaries (e.g. `claude` subprocess).
    """

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Return the human-readable name of this adapter (e.g. 'gemini', 'claude')."""

    @abstractmethod
    def send_message(
        self,
        user_message: str,
        system_prompt: str = "",
    ) -> AgentResponse:
        """Send a message to the underlying AI agent and return the response.

        Parameters
        ----------
        user_message:
            The user-facing prompt or question to send to the agent.
        system_prompt:
            An optional system-level instruction to inject before the user message.
            Adapters should pass this as a system instruction, system prompt flag,
            or prepended context — depending on the target agent's capabilities.

        Returns
        -------
        AgentResponse
            A uniform response object containing the agent's text output,
            latency, model name, and raw response data.

        Raises
        ------
        ValueError
            If the user_message is empty.
        RuntimeError
            If the underlying agent call fails.
        """

    def _validate_message(self, user_message: str) -> None:
        """Shared input validation for all adapters."""
        if not user_message or not user_message.strip():
            raise ValueError("user_message must not be empty")

    def _timed_call(self, fn: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
        """Execute a callable and return (result, elapsed_seconds)."""
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
