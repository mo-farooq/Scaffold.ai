"""Status Dashboard Screen — Progress overview, analytics, and timeline."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static


class StatusScreen(Screen):
    """Full-screen progress dashboard with milestones, analytics, and timeline."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="status-container"):
            yield Static("", id="status-header")
            yield Static("", id="progress-section")
            yield Static("", id="analytics-section")
            yield Static("", id="timeline-section")
            yield Button("← Back", id="back-button", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        """Populate dashboard with current data."""
        self._refresh_dashboard()

    def on_screen_resume(self) -> None:
        """Refresh data when returning to this screen."""
        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """Rebuild all dashboard sections from controller data."""
        status = self.app.controller.get_status()

        if not status.get("active"):
            self.query_one("#status-header", Static).update(
                "[bold]No active project.[/bold]"
            )
            return

        # Header
        self.query_one("#status-header", Static).update(
            f"[bold cyan]📊 Progress Dashboard[/bold cyan]\n"
            f"[dim]{status['project_description']}[/dim]"
        )

        # Progress section
        progress_lines = ["[bold]📋 Milestone Progress[/bold]\n"]
        milestones = status.get("milestones", [])
        current_idx = status.get("current_index", 0)
        state = status.get("state", "IN_PROGRESS")

        for i, m in enumerate(milestones):
            if state == "COMPLETED" or i < current_idx:
                progress_lines.append(f"  [green]✅ {i + 1}. {m}[/green]")
            elif i == current_idx:
                progress_lines.append(f"  [bold cyan]🔵 {i + 1}. {m} ◄ CURRENT[/bold cyan]")
            else:
                progress_lines.append(f"  [dim]⬜ {i + 1}. {m}[/dim]")

        pct = status.get("progress_percentage", 0)
        bar_filled = int(pct / 5)
        bar_empty = 20 - bar_filled
        progress_bar = f"  [green]{'█' * bar_filled}[/green][dim]{'░' * bar_empty}[/dim] {pct:.0f}%"
        progress_lines.append(f"\n{progress_bar}")

        self.query_one("#progress-section", Static).update("\n".join(progress_lines))

        # Analytics section
        analytics = self.app.controller.get_analytics()
        analytics_text = (
            f"[bold]📈 Learning Analytics[/bold]\n\n"
            f"  [bold]Total Attempts:[/bold]      {analytics.total_attempts}\n"
            f"  [bold]Passed:[/bold]               {analytics.successful_evaluations}\n"
            f"  [bold]Failed:[/bold]               {analytics.failed_evaluations}\n"
            f"  [bold]Pass Rate:[/bold]            {analytics.pass_rate:.1f}%\n"
            f"  [bold]Total Time:[/bold]           {analytics.total_duration_seconds:.0f}s\n"
            f"  [bold]Adapter:[/bold]              {status.get('adapter', 'gemini')}"
        )
        self.query_one("#analytics-section", Static).update(analytics_text)

        # Timeline section
        timeline = self.app.controller.get_timeline()
        if timeline.entries:
            timeline_lines = ["[bold]📚 Learning Timeline[/bold]\n"]
            for entry in timeline.entries:
                outcome_icon = "✅" if entry.reflection_outcome == "PASSED" else "🔄"
                timeline_lines.append(
                    f"  {outcome_icon} [bold]M{entry.milestone_index + 1}:[/bold] "
                    f"{entry.concept_learned}"
                )
                if entry.files_modified:
                    timeline_lines.append(
                        f"     [dim]Files: {', '.join(entry.files_modified)}[/dim]"
                    )
            self.query_one("#timeline-section", Static).update("\n".join(timeline_lines))
        else:
            self.query_one("#timeline-section", Static).update(
                "[bold]📚 Learning Timeline[/bold]\n\n  [dim]No concepts recorded yet.[/dim]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle back button."""
        if event.button.id == "back-button":
            self.app.pop_screen()
