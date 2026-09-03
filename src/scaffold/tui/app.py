"""Scaffold.ai TUI — Main Application Shell.

The root Textual App class that manages screens, keybindings, and theming.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from scaffold.controller import ScaffoldController
from scaffold.tui.screens.session import SessionScreen
from scaffold.tui.screens.setup import SetupScreen
from scaffold.tui.screens.status import StatusScreen
from scaffold.tui.screens.welcome import WelcomeScreen


class ScaffoldApp(App):
    """Scaffold.ai — Interactive AI-Powered Learning Harness."""

    TITLE = "Scaffold.ai"
    SUB_TITLE = "Learn by building. Build by learning."
    CSS_PATH = "scaffold.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+n", "new_project", "New Project", show=True),
        Binding("ctrl+s", "show_status", "Status", show=True),
        Binding("ctrl+h", "go_home", "Home", show=True),
    ]

    SCREENS = {
        "welcome": WelcomeScreen,
        "setup": SetupScreen,
        "session": SessionScreen,
        "status": StatusScreen,
    }

    def __init__(self) -> None:
        super().__init__()
        self.controller = ScaffoldController()

    def on_mount(self) -> None:
        """Show the welcome screen on startup."""
        self.push_screen("welcome")

    def action_new_project(self) -> None:
        """Navigate to the project setup screen."""
        self.push_screen("setup")

    def action_show_status(self) -> None:
        """Navigate to the status dashboard."""
        if self.controller.session is not None:
            self.push_screen("status")
        else:
            self.notify("No active project. Start or resume a project first.", severity="warning")

    def action_go_home(self) -> None:
        """Navigate back to the welcome screen."""
        while len(self.screen_stack) > 1:
            self.pop_screen()
        if self.screen.id != "welcome":
            self.push_screen("welcome")
