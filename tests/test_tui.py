"""Tests for Scaffold.ai TUI Application using Textual's pilot framework."""

from __future__ import annotations

import pytest

from textual.geometry import Size

from scaffold.tui.app import ScaffoldApp


@pytest.mark.asyncio
class TestTUIAppStructure:
    async def test_app_starts_with_welcome_screen(self) -> None:
        """The app should show the welcome screen on startup."""
        app = ScaffoldApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            # The welcome banner should be visible on the pushed screen
            banner = app.screen.query_one("#welcome-banner")
            assert banner is not None

    async def test_welcome_has_all_buttons(self) -> None:
        """Welcome screen should have all navigation buttons."""
        app = ScaffoldApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            screen = app.screen
            assert screen.query_one("#btn-new") is not None
            assert screen.query_one("#btn-resume") is not None
            assert screen.query_one("#btn-status") is not None
            assert screen.query_one("#btn-quit") is not None

    async def test_new_project_navigates_to_setup(self) -> None:
        """Pressing the 'Start New Project' button should push the setup screen."""
        app = ScaffoldApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            # Press the button via its action
            await pilot.press("enter")  # Focus is on first button (New Project)
            await pilot.pause()
            # Verify setup screen is now active
            project_input = app.screen.query_one("#project-input")
            assert project_input is not None

    async def test_ctrl_q_quits(self) -> None:
        """Pressing Ctrl+Q should exit the app."""
        app = ScaffoldApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await pilot.press("ctrl+q")
