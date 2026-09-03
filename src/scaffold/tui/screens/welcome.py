"""Welcome Screen — Landing page with branded banner and navigation menu."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


BANNER = r"""
╔══════════════════════════════════════════════╗
║           🏗️  S C A F F O L D . A I          ║
║                                              ║
║      Learn by building. Build by learning.   ║
╚══════════════════════════════════════════════╝
"""


class WelcomeScreen(Screen):
    """Welcome screen with app branding and navigation menu."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="welcome-container"):
            yield Static(BANNER, id="welcome-banner")
            with Vertical(id="welcome-menu"):
                yield Button("🆕  Start New Project", id="btn-new", variant="primary")
                yield Button(
                    "📂  Resume Existing Project",
                    id="btn-resume",
                    variant="default",
                    disabled=not self.app.controller.has_existing_session,
                )
                yield Button("📊  View Progress Dashboard", id="btn-status", variant="default")
                yield Button("❌  Quit", id="btn-quit", variant="error")
        yield Footer()

    def on_screen_resume(self) -> None:
        """Refresh resume button state when returning to this screen."""
        btn = self.query_one("#btn-resume", Button)
        btn.disabled = not self.app.controller.has_existing_session

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses."""
        if event.button.id == "btn-new":
            self.app.push_screen("setup")
        elif event.button.id == "btn-resume":
            try:
                self.app.controller.resume_project()
                self.app.push_screen("session")
            except FileNotFoundError:
                self.notify("No saved session found.", severity="error")
        elif event.button.id == "btn-status":
            if self.app.controller.has_existing_session:
                if self.app.controller.session is None:
                    self.app.controller.resume_project()
                self.app.push_screen("status")
            else:
                self.notify("No project to show. Start a new project first.", severity="warning")
        elif event.button.id == "btn-quit":
            self.app.exit()
