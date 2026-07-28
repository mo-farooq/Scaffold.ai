"""Tests for Scaffold.ai Reflection Evaluator Engine."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scaffold.evaluator import EvaluationResult, _clean_json_text, evaluate_answer


class TestCleanJsonText:
    def test_clean_json_text(self) -> None:
        raw = "```json\n{\"passed\": true, \"score\": 0.9}\n```"
        assert _clean_json_text(raw) == '{"passed": true, "score": 0.9}'


class TestEvaluationResultModel:
    def test_evaluation_result_normalization(self) -> None:
        res_pass = EvaluationResult(passed=True, score=0.9, feedback="Great job!")
        assert res_pass.suggested_action == "ADVANCE"
        assert res_pass.score == 0.9

        res_fail = EvaluationResult(passed=False, score=0.2, feedback="Needs work", hint="Think about X")
        assert res_fail.suggested_action == "RETRY"
        assert res_fail.hint == "Think about X"

    def test_score_clamping(self) -> None:
        res_over = EvaluationResult(passed=True, score=1.5, feedback="Great")
        assert res_over.score == 1.0

        res_under = EvaluationResult(passed=False, score=-0.5, feedback="Wrong")
        assert res_under.score == 0.0


class TestEvaluatorInputValidation:
    def test_empty_answer_raises(self) -> None:
        with pytest.raises(ValueError, match="student_answer must not be empty"):
            evaluate_answer(student_answer="  ", question="What is a class?")

    def test_empty_question_raises(self) -> None:
        with pytest.raises(ValueError, match="question must not be empty"):
            evaluate_answer(student_answer="A class is a blueprint.", question="   ")

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr("scaffold.evaluator.load_dotenv", lambda: None)
        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            evaluate_answer(student_answer="Answer", question="Question")


class TestEvaluatorResponseParsing:
    @patch("scaffold.evaluator.genai.Client")
    def test_mocked_pass_evaluation(
        self, mock_client_cls: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "fake_key")

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = json_str = (
            '{"passed": true, "score": 0.95, "feedback": "Excellent reasoning!", '
            '"hint": null, "suggested_action": "ADVANCE"}'
        )
        mock_client.models.generate_content.return_value = mock_response

        res = evaluate_answer("Correct explanation of dataclass vs dict", "Why dataclass?")
        assert res.passed is True
        assert res.score == 0.95
        assert res.suggested_action == "ADVANCE"

    @patch("scaffold.evaluator.genai.Client")
    def test_mocked_retry_evaluation(
        self, mock_client_cls: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "fake_key")

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = (
            '{"passed": false, "score": 0.3, "feedback": "Incorrect assumption.", '
            '"hint": "Consider field type safety.", "suggested_action": "RETRY"}'
        )
        mock_client.models.generate_content.return_value = mock_response

        res = evaluate_answer("Because it is 100x faster", "Why dataclass?")
        assert res.passed is False
        assert res.score == 0.3
        assert res.suggested_action == "RETRY"
        assert res.hint == "Consider field type safety."


@pytest.mark.integration
class TestLiveEvaluatorIntegration:
    def test_live_answer_evaluation(self) -> None:
        import os

        from dotenv import load_dotenv
        load_dotenv()
        if not os.environ.get("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        result = evaluate_answer(
            student_answer="Dataclasses enforce field types and names, avoiding typo crashes.",
            question="Why use a dataclass over a raw dictionary?",
        )
        assert isinstance(result, EvaluationResult)
        assert isinstance(result.passed, bool)
        assert 0.0 <= result.score <= 1.0
