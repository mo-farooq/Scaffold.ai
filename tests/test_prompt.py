"""Structural tests for the Learning Mode prompt wrapper."""

from __future__ import annotations

import pytest

from scaffold.prompt import MilestoneContext, build_prompt


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture()
def todo_milestones() -> list[str]:
    return [
        "Data model — define the Task dataclass",
        "CRUD API — add, list, update, delete",
        "CLI interface — argparse commands",
        "Persistence — JSON file read/write",
    ]


@pytest.fixture()
def todo_description() -> str:
    return "A command-line Todo app in Python."


def _make_ctx(
    description: str,
    milestones: list[str],
    index: int = 0,
) -> MilestoneContext:
    return MilestoneContext(
        project_description=description,
        milestones=milestones,
        current_index=index,
    )


# ── Validation tests ────────────────────────────────────────────────────


class TestMilestoneContextValidation:
    def test_empty_description_raises(self, todo_milestones: list[str]) -> None:
        with pytest.raises(ValueError, match="project_description"):
            _make_ctx("   ", todo_milestones)

    def test_empty_milestones_raises(self, todo_description: str) -> None:
        with pytest.raises(ValueError, match="milestones"):
            _make_ctx(todo_description, [])

    def test_index_too_high_raises(
        self, todo_description: str, todo_milestones: list[str]
    ) -> None:
        with pytest.raises(IndexError, match="out of range"):
            _make_ctx(todo_description, todo_milestones, index=99)

    def test_negative_index_raises(
        self, todo_description: str, todo_milestones: list[str]
    ) -> None:
        with pytest.raises(IndexError, match="out of range"):
            _make_ctx(todo_description, todo_milestones, index=-1)


# ── Structural tests ────────────────────────────────────────────────────


class TestPromptStructure:
    """Verify that the generated prompt contains all required sections."""

    @pytest.fixture()
    def prompt_first(
        self, todo_description: str, todo_milestones: list[str]
    ) -> str:
        ctx = _make_ctx(todo_description, todo_milestones, index=0)
        return build_prompt(ctx)

    @pytest.fixture()
    def prompt_middle(
        self, todo_description: str, todo_milestones: list[str]
    ) -> str:
        ctx = _make_ctx(todo_description, todo_milestones, index=2)
        return build_prompt(ctx)

    # -- Top-level heading
    def test_has_title(self, prompt_first: str) -> None:
        assert "# Scaffold.ai" in prompt_first

    # -- Role section
    def test_has_role_section(self, prompt_first: str) -> None:
        assert "## Role" in prompt_first
        assert "tutor" in prompt_first.lower()

    # -- Project overview
    def test_has_project_overview(self, prompt_first: str) -> None:
        assert "## Project Overview" in prompt_first
        assert "Todo" in prompt_first

    # -- Milestone section
    def test_has_milestone_section(self, prompt_first: str) -> None:
        assert "## Milestone" in prompt_first

    def test_current_milestone_highlighted(self, prompt_first: str) -> None:
        assert "👉" in prompt_first

    def test_shows_progress_label(self, prompt_first: str) -> None:
        assert "Milestone 1 of 4" in prompt_first

    def test_completed_milestones_mentioned_for_later_index(
        self, prompt_middle: str
    ) -> None:
        assert "already completed" in prompt_middle

    def test_no_completed_section_for_first_milestone(
        self, prompt_first: str
    ) -> None:
        assert "already completed" not in prompt_first

    # -- Protocol rules
    def test_has_explain_first_rule(self, prompt_first: str) -> None:
        assert "Explain first" in prompt_first

    def test_has_stay_in_scope_rule(self, prompt_first: str) -> None:
        assert "Stay in scope" in prompt_first

    def test_has_one_concept_rule(self, prompt_first: str) -> None:
        assert "One concept at a time" in prompt_first

    def test_has_tradeoffs_rule(self, prompt_first: str) -> None:
        assert "trade-off" in prompt_first.lower() or "alternative" in prompt_first.lower()

    def test_has_reflection_rule(self, prompt_first: str) -> None:
        assert "reflective question" in prompt_first.lower()

    def test_has_stop_instruction(self, prompt_first: str) -> None:
        assert "STOP" in prompt_first

    # -- Formatting section
    def test_has_formatting_section(self, prompt_first: str) -> None:
        assert "## Formatting" in prompt_first

    def test_mentions_reflective_question_heading(self, prompt_first: str) -> None:
        assert "Reflective Question" in prompt_first


# ── Edge-case tests ──────────────────────────────────────────────────────


class TestEdgeCases:
    def test_single_milestone(self, todo_description: str) -> None:
        ctx = _make_ctx(todo_description, ["Only milestone"], index=0)
        prompt = build_prompt(ctx)
        assert "Milestone 1 of 1" in prompt
        assert "already completed" not in prompt

    def test_last_milestone(
        self, todo_description: str, todo_milestones: list[str]
    ) -> None:
        ctx = _make_ctx(todo_description, todo_milestones, index=3)
        prompt = build_prompt(ctx)
        assert "Milestone 4 of 4" in prompt
        assert "already completed" in prompt

    def test_prompt_is_nonempty_string(
        self, todo_description: str, todo_milestones: list[str]
    ) -> None:
        ctx = _make_ctx(todo_description, todo_milestones, index=0)
        prompt = build_prompt(ctx)
        assert isinstance(prompt, str)
        assert len(prompt) > 200  # sanity: prompt should be substantial
