"""Setup Screen — Project idea input and milestone generation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Markdown, Static
from textual.worker import Worker, get_current_worker


class SetupScreen(Screen):
    """Screen for entering a project idea and generating milestones."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="setup-container"):
            yield Static(
                "## 🆕 New Learning Project\n\nDescribe the project you want to build:",
                id="setup-title",
            )
            with Vertical(id="setup-input-area"):
                yield Input(
                    placeholder="e.g. A REST API with FastAPI and PostgreSQL for a todo app...",
                    id="project-input",
                )
            yield Static("", id="loading-text", classes="loading-indicator")
            yield Markdown("", id="milestone-panel")
            with Vertical(id="setup-buttons"):
                yield Button("🚀 Start Learning", id="btn-start", variant="primary", disabled=True)
                yield Button("🔄 Regenerate", id="btn-regen", variant="default", disabled=True)
                yield Button("← Back", id="btn-back", variant="default")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the project input."""
        description = event.value.strip()
        if description:
            self._generate_milestones(description)

    def _generate_milestones(self, description: str) -> None:
        """Run milestone generation in a background worker."""
        loading = self.query_one("#loading-text", Static)
        loading.update("⏳ Generating milestones... (this may take a few seconds)")
        self.query_one("#btn-start", Button).disabled = True
        self.query_one("#btn-regen", Button).disabled = True

        self.run_worker(
            self._do_generate(description),
            name="generate_milestones",
            exclusive=True,
        )

    async def _do_generate(self, description: str) -> None:
        """Background worker that calls the controller to generate milestones."""
        try:
            session = self.app.controller.init_project(description)

            # Build milestone display
            lines = ["## 📋 Generated Milestones\n"]
            for i, m in enumerate(session.milestones, 1):
                lines.append(f"{i}. **{m}**")
            lines.append(f"\n*{len(session.milestones)} milestones generated for your project.*")
            md_text = "\n".join(lines)

            self.app.call_from_thread(self._update_milestone_display, md_text)
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _update_milestone_display(self, md_text: str) -> None:
        """Update the UI with generated milestones (called from main thread)."""
        self.query_one("#loading-text", Static).update("")
        self.query_one("#milestone-panel", Markdown).update(md_text)
        self.query_one("#btn-start", Button).disabled = False
        self.query_one("#btn-regen", Button).disabled = False

    def _show_error(self, error_msg: str) -> None:
        """Display an error message."""
        self.query_one("#loading-text", Static).update("")
        self.notify(f"Error: {error_msg}", severity="error")
        self.query_one("#btn-regen", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-start":
            self.app.push_screen("session")
        elif event.button.id == "btn-regen":
            input_widget = self.query_one("#project-input", Input)
            description = input_widget.value.strip()
            if description:
                self._generate_milestones(description)
        elif event.button.id == "btn-back":
            self.app.pop_screen()
