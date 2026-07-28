"""Tests for Scaffold.ai Session State Machine & Local Storage."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from scaffold.prompt import MilestoneContext
from scaffold.session import (
    Session,
    SessionState,
    advance_milestone,
    get_current_context,
    init_session,
    load_session,
    reset_session,
    save_session,
)


@pytest.fixture()
def sample_description() -> str:
    return "A command-line Todo app in Python."


@pytest.fixture()
def sample_milestones() -> list[str]:
    return [
        "1. Data model — Task and TodoList",
        "2. CRUD API — add, list, update, delete",
        "3. CLI interface — argparse integration",
        "4. Persistence — JSON file storage",
    ]


class TestSessionModelValidation:
    def test_empty_description_raises(self, sample_milestones: list[str]) -> None:
        with pytest.raises(ValueError, match="project_description must not be empty"):
            Session(project_description="   ", milestones=sample_milestones)

    def test_empty_milestones_raises(self, sample_description: str) -> None:
        with pytest.raises(ValueError, match="milestones must contain at least one item"):
            Session(project_description=sample_description, milestones=[])

    def test_negative_index_raises(
        self, sample_description: str, sample_milestones: list[str]
    ) -> None:
        with pytest.raises(IndexError, match="current_index must not be negative"):
            Session(
                project_description=sample_description,
                milestones=sample_milestones,
                current_index=-1,
            )

    def test_out_of_bounds_index_sets_completed(
        self, sample_description: str, sample_milestones: list[str]
    ) -> None:
        session = Session(
            project_description=sample_description,
            milestones=sample_milestones,
            current_index=10,
        )
        assert session.state == SessionState.COMPLETED
        assert session.is_completed is True
        assert session.progress_percentage == 100.0


class TestSessionPersistence:
    def test_init_and_load_session(
        self, sample_description: str, sample_milestones: list[str], tmp_path: Path
    ) -> None:
        session = init_session(
            sample_description, sample_milestones, session_dir=tmp_path
        )
        assert session.project_description == sample_description
        assert session.current_index == 0
        assert session.state == SessionState.IN_PROGRESS

        # Verify file exists
        session_file = tmp_path / "session.json"
        assert session_file.exists()

        # Load back
        loaded = load_session(session_dir=tmp_path)
        assert loaded.project_description == sample_description
        assert loaded.milestones == sample_milestones
        assert loaded.current_index == 0
        assert loaded.state == SessionState.IN_PROGRESS

    def test_load_nonexistent_session_raises_filenotfound(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="No active session found"):
            load_session(session_dir=tmp_path)

    def test_load_corrupted_json_raises_valueerror(self, tmp_path: Path) -> None:
        session_file = tmp_path / "session.json"
        session_file.write_text("This is corrupted JSON string {", encoding="utf-8")

        with pytest.raises(ValueError, match="Corrupted or invalid session file"):
            load_session(session_dir=tmp_path)


class TestSessionStateTransitions:
    def test_advance_milestones_until_completion(
        self, sample_description: str, sample_milestones: list[str], tmp_path: Path
    ) -> None:
        session = init_session(
            sample_description, sample_milestones, session_dir=tmp_path
        )
        assert session.current_index == 0
        assert session.progress_percentage == 0.0

        # Advance to 1
        session = advance_milestone(session, session_dir=tmp_path)
        assert session.current_index == 1
        assert session.state == SessionState.IN_PROGRESS
        assert session.progress_percentage == 25.0

        # Advance to 2
        session = advance_milestone(session, session_dir=tmp_path)
        assert session.current_index == 2
        assert session.progress_percentage == 50.0

        # Advance to 3
        session = advance_milestone(session, session_dir=tmp_path)
        assert session.current_index == 3
        assert session.progress_percentage == 75.0

        # Advance to 4 (completion)
        session = advance_milestone(session, session_dir=tmp_path)
        assert session.current_index == 4
        assert session.state == SessionState.COMPLETED
        assert session.is_completed is True
        assert session.progress_percentage == 100.0

    def test_get_current_context_conversion(
        self, sample_description: str, sample_milestones: list[str]
    ) -> None:
        session = Session(
            project_description=sample_description,
            milestones=sample_milestones,
            current_index=1,
        )
        ctx = get_current_context(session)
        assert isinstance(ctx, MilestoneContext)
        assert ctx.project_description == sample_description
        assert ctx.current_index == 1
        assert ctx.current_milestone == sample_milestones[1]

    def test_reset_session_removes_file(
        self, sample_description: str, sample_milestones: list[str], tmp_path: Path
    ) -> None:
        init_session(sample_description, sample_milestones, session_dir=tmp_path)
        assert (tmp_path / "session.json").exists()

        assert reset_session(session_dir=tmp_path) is True
        assert not (tmp_path / "session.json").exists()

        # Resetting non-existent session returns False
        assert reset_session(session_dir=tmp_path) is False
