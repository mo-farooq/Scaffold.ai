"""Adapter Factory & Registry for Scaffold.ai.

Provides a factory function `get_adapter()` and a registry of available
AI agent adapters (Gemini, Claude Code CLI).
"""

from __future__ import annotations

from typing import Any

from scaffold.adapters.base import AgentAdapter, AgentResponse
from scaffold.adapters.claude import ClaudeAdapter
from scaffold.adapters.gemini import GeminiAdapter

_ADAPTER_REGISTRY: dict[str, type[AgentAdapter]] = {
    "gemini": GeminiAdapter,
    "claude": ClaudeAdapter,
}


def list_available_adapters() -> list[str]:
    """Return the names of all registered agent adapters.

    Returns
    -------
    list[str]
        Sorted list of adapter names (e.g. ['claude', 'gemini']).
    """
    return sorted(_ADAPTER_REGISTRY.keys())


def get_adapter(adapter_name: str = "gemini", **kwargs: Any) -> AgentAdapter:
    """Instantiate and return an agent adapter by name.

    Parameters
    ----------
    adapter_name:
        The name of the adapter to create ('gemini' or 'claude').
    **kwargs:
        Additional keyword arguments forwarded to the adapter constructor
        (e.g. api_key, model_name, cli_path, timeout_seconds).

    Returns
    -------
    AgentAdapter
        An instantiated adapter ready for `send_message()` calls.

    Raises
    ------
    ValueError
        If the adapter_name is not registered.
    """
    name = adapter_name.strip().lower()
    adapter_cls = _ADAPTER_REGISTRY.get(name)
    if adapter_cls is None:
        available = ", ".join(list_available_adapters())
        raise ValueError(
            f"Unknown adapter '{adapter_name}'. Available adapters: {available}"
        )
    return adapter_cls(**kwargs)


__all__ = [
    "AgentAdapter",
    "AgentResponse",
    "ClaudeAdapter",
    "GeminiAdapter",
    "get_adapter",
    "list_available_adapters",
]
