"""Tests for Prompt Protocol Validator."""

from __future__ import annotations

from scaffold.validator import ProtocolValidationResult, validate_protocol


class TestProtocolValidator:
    def test_empty_response_fails(self) -> None:
        res = validate_protocol("   ")
        assert res.passed is False
        assert res.overall_score == 0.0

    def test_valid_learning_mode_response(self) -> None:
        sample_output = (
            "Welcome! The goal of this milestone is to define the Task dataclass.\n\n"
            "Here is the data structure:\n"
            "```python\n@dataclass\nclass Task:\n    title: str\n```\n\n"
            "We chose a dataclass instead of a dictionary for type safety.\n\n"
            "### Milestone Check\n* [x] Task dataclass defined.\n\n"
            "### 🤔 Reflective Question\nWhy is type safety useful?"
        )
        res = validate_protocol(sample_output)
        assert isinstance(res, ProtocolValidationResult)
        assert res.passed is True
        assert res.overall_score >= 0.8

    def test_missing_reflection_question_fails(self) -> None:
        sample_output = (
            "Here is the code for the entire app:\n"
            "```python\nprint('hello')\n```"
        )
        res = validate_protocol(sample_output)
        assert res.passed is False
