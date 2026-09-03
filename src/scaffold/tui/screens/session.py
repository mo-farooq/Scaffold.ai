"""Learning Session Screen — The main interactive learning view.

Split layout: conversation panel (left) + milestone sidebar (right)
with input bar at bottom.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, RichLog, Static


class SessionScreen(Screen):
    """Main learning session screen with chat panel and milestone sidebar."""

    BINDINGS = [
        ("ctrl+t", "show_timeline", "Timeline"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="session-layout"):
            # Left: Chat/conversation panel
            with Vertical(id="chat-panel"):
                yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
            # Right: Milestone sidebar
            with Vertical(id="sidebar"):
                yield Static("📋 MILESTONES", classes="section-title")
                yield Static("", id="milestone-list")
                yield Static("📊 STATS", classes="section-title")
                yield Static("", id="stats-panel")
        yield Input(placeholder="Type your message or reflection answer...", id="message-input")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the session view with current state."""
        self._refresh_sidebar()
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Display an initial welcome message in the chat log."""
        log = self.query_one("#chat-log", RichLog)
        session = self.app.controller.session
        if session is None:
            return

        log.write(
            f"[bold cyan]🏗️ Scaffold.ai — Learning Session[/bold cyan]\n"
            f"[dim]Project: {session.project_description}[/dim]\n"
            f"[dim]Progress: {session.progress_percentage:.0f}% "
            f"(Milestone {session.current_index + 1}/{len(session.milestones)})[/dim]\n"
        )
        log.write(
            f"[bold green]▶ Current Milestone:[/bold green] "
            f"[bold]{session.current_milestone}[/bold]\n"
        )
        log.write(
            "[dim]Type a message to start learning, or type your reflection answer.[/dim]\n"
            "[dim]Press Ctrl+S for status, Ctrl+H for home, Ctrl+Q to quit.[/dim]\n"
        )

    def _refresh_sidebar(self) -> None:
        """Update the milestone list and stats in the sidebar."""
        session = self.app.controller.session
        if session is None:
            return

        # Milestone list
        lines = []
        for i, m in enumerate(session.milestones):
            if i < session.current_index:
                lines.append(f"[green]✅ {i + 1}. {m}[/green]")
            elif i == session.current_index:
                lines.append(f"[bold cyan]🔵 {i + 1}. {m} ◄[/bold cyan]")
            else:
                lines.append(f"[dim]⬜ {i + 1}. {m}[/dim]")

        self.query_one("#milestone-list", Static).update("\n".join(lines))

        # Stats
        analytics = self.app.controller.get_analytics()
        stats_text = (
            f"[bold]Pass Rate:[/bold] {analytics.pass_rate:.0f}%\n"
            f"[bold]Attempts:[/bold] {analytics.total_attempts}\n"
            f"[bold]Progress:[/bold] {session.progress_percentage:.0f}%"
        )
        self.query_one("#stats-panel", Static).update(stats_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission from the input bar."""
        message = event.value.strip()
        if not message:
            return

        event.input.value = ""
        log = self.query_one("#chat-log", RichLog)

        # Display user message
        log.write(f"\n[bold yellow]👤 You:[/bold yellow] {message}\n")

        controller = self.app.controller

        if controller.is_awaiting_reflection:
            # Submit as reflection answer
            log.write("[dim]⏳ Evaluating your answer...[/dim]")
            self.run_worker(
                self._do_submit_answer(message),
                name="submit_answer",
                exclusive=True,
            )
        else:
            # Send as regular message to AI agent
            log.write("[dim]⏳ Thinking...[/dim]")
            self.run_worker(
                self._do_send_message(message),
                name="send_message",
                exclusive=True,
            )

    async def _do_send_message(self, message: str) -> None:
        """Background worker: send message to AI agent."""
        try:
            response = self.app.controller.send_message(message)
            self.app.call_from_thread(self._display_agent_response, response.content)
        except Exception as e:
            self.app.call_from_thread(self._display_error, str(e))

    async def _do_submit_answer(self, answer: str) -> None:
        """Background worker: submit reflection answer."""
        try:
            result = self.app.controller.submit_answer(answer)
            self.app.call_from_thread(self._display_evaluation_result, result)
        except Exception as e:
            self.app.call_from_thread(self._display_error, str(e))

    def _display_agent_response(self, content: str) -> None:
        """Display AI agent response in the chat log."""
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold blue]🤖 AI Tutor:[/bold blue]\n{content}\n")
        self._refresh_sidebar()

    def _display_evaluation_result(self, result: object) -> None:
        """Display evaluation feedback in the chat log."""
        log = self.query_one("#chat-log", RichLog)

        if result.passed:  # type: ignore[union-attr]
            log.write(
                f"\n[bold green]✅ PASSED[/bold green] "
                f"(Score: {result.score:.0%})\n"  # type: ignore[union-attr]
                f"[green]{result.feedback}[/green]\n"  # type: ignore[union-attr]
            )
            session = self.app.controller.session
            if session and not self.app.controller.is_completed:
                log.write(
                    f"\n[bold cyan]▶ Advancing to:[/bold cyan] "
                    f"[bold]{session.current_milestone}[/bold]\n"
                    f"[dim]Type a message to continue learning.[/dim]\n"
                )
            elif self.app.controller.is_completed:
                log.write(
                    "\n[bold green]🎉 CONGRATULATIONS![/bold green]\n"
                    "[green]You have completed all milestones! "
                    "Press Ctrl+S to view your full progress dashboard.[/green]\n"
                )
        else:
            log.write(
                f"\n[bold red]🔄 RETRY[/bold red] "
                f"(Score: {result.score:.0%})\n"  # type: ignore[union-attr]
                f"[yellow]{result.feedback}[/yellow]\n"  # type: ignore[union-attr]
            )
            if result.hint:  # type: ignore[union-attr]
                log.write(f"[dim]💡 Hint: {result.hint}[/dim]\n")  # type: ignore[union-attr]
            log.write("[dim]Try again with your refined answer.[/dim]\n")

        self._refresh_sidebar()

    def _display_error(self, error_msg: str) -> None:
        """Display an error in the chat log."""
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold red]❌ Error:[/bold red] {error_msg}\n")

    def action_show_timeline(self) -> None:
        """Show timeline via status screen."""
        self.app.push_screen("status")
