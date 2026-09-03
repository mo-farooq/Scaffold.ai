"""Tests for ScaffoldController — UI-agnostic business logic layer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scaffold.controller import ScaffoldController
from scaffold.evaluator import EvaluationResult


class TestControllerInit:
    def test_no_session_by_default(self, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        assert ctrl.session is None
        assert not ctrl.has_existing_session
        assert not ctrl.is_awaiting_reflection
        assert not ctrl.is_completed

    def test_available_adapters(self, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        adapters = ctrl.available_adapters
        assert "gemini" in adapters
        assert "claude" in adapters


class TestControllerProjectLifecycle:
    @patch("scaffold.controller.generate_milestones")
    def test_init_project(self, mock_gen: MagicMock, tmp_path: Path) -> None:
        mock_gen.return_value = ["Milestone A", "Milestone B", "Milestone C"]
        ctrl = ScaffoldController(project_dir=tmp_path)

        session = ctrl.init_project("Build a todo app")
        assert session is not None
        assert session.project_description == "Build a todo app"
        assert len(session.milestones) == 3
        assert ctrl.has_existing_session

    @patch("scaffold.controller.generate_milestones")
    def test_resume_project(self, mock_gen: MagicMock, tmp_path: Path) -> None:
        mock_gen.return_value = ["M1", "M2"]
        ctrl = ScaffoldController(project_dir=tmp_path)
        ctrl.init_project("Test project")

        # Create a new controller and resume
        ctrl2 = ScaffoldController(project_dir=tmp_path)
        session = ctrl2.resume_project()
        assert session.project_description == "Test project"
        assert len(session.milestones) == 2

    @patch("scaffold.controller.generate_milestones")
    def test_reset_project(self, mock_gen: MagicMock, tmp_path: Path) -> None:
        mock_gen.return_value = ["M1"]
        ctrl = ScaffoldController(project_dir=tmp_path)
        ctrl.init_project("Test")
        assert ctrl.has_existing_session

        ctrl.reset_project()
        assert ctrl.session is None
        assert not ctrl.has_existing_session

    def test_resume_nonexistent_raises(self, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        with pytest.raises(FileNotFoundError):
            ctrl.resume_project()


class TestControllerStatus:
    def test_status_no_session(self, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        status = ctrl.get_status()
        assert status["active"] is False

    @patch("scaffold.controller.generate_milestones")
    def test_status_with_session(self, mock_gen: MagicMock, tmp_path: Path) -> None:
        mock_gen.return_value = ["M1", "M2", "M3"]
        ctrl = ScaffoldController(project_dir=tmp_path)
        ctrl.init_project("Test app")

        status = ctrl.get_status()
        assert status["active"] is True
        assert status["total_milestones"] == 3
        assert status["current_index"] == 0
        assert status["progress_percentage"] == 0.0


class TestControllerMessageFlow:
    @patch("scaffold.controller.generate_milestones")
    def test_send_message_no_session_raises(self, mock_gen: MagicMock, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        with pytest.raises(RuntimeError, match="No active session"):
            ctrl.send_message("Hello")

    def test_submit_answer_no_session_raises(self, tmp_path: Path) -> None:
        ctrl = ScaffoldController(project_dir=tmp_path)
        with pytest.raises(RuntimeError, match="No active session"):
            ctrl.submit_answer("My answer")
