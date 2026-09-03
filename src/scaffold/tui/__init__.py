"""Scaffold.ai TUI — Interactive Terminal Application.

Launch with: scaffold (after pip install) or uv run python -m scaffold.tui
"""

from __future__ import annotations

from scaffold.tui.app import ScaffoldApp


def main() -> None:
    """Entry point for the scaffold console script."""
    app = ScaffoldApp()
    app.run()


__all__ = ["ScaffoldApp", "main"]
