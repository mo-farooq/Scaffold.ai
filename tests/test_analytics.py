"""Tests for Reflection Analytics Engine."""

from __future__ import annotations

from pathlib import Path

from scaffold.analytics import AnalyticsEngine
from scaffold.evaluator import EvaluationResult


class TestAnalyticsEngine:
    def test_record_attempt(self, tmp_path: Path) -> None:
        engine = AnalyticsEngine(storage_dir=tmp_path)
        assert engine.data.total_attempts == 0

        res_pass = EvaluationResult(passed=True, score=0.9, feedback="Great job!")
        rec1 = engine.record_attempt(
            milestone_index=0,
            question="Why dataclass?",
            student_answer="Type safety",
            result=res_pass,
            duration_seconds=30.0,
        )
        assert rec1.passed is True
        assert engine.data.total_attempts == 1
        assert engine.data.successful_evaluations == 1
        assert engine.data.pass_rate == 100.0

        res_fail = EvaluationResult(passed=False, score=0.3, feedback="Wrong speed assumption", hint="Think about types")
        rec2 = engine.record_attempt(
            milestone_index=0,
            question="Why dataclass?",
            student_answer="For 10x speed",
            result=res_fail,
            duration_seconds=15.0,
        )
        assert rec2.passed is False
        assert engine.data.total_attempts == 2
        assert engine.data.failed_evaluations == 1
        assert engine.data.pass_rate == 50.0

        # Reload from disk
        reloaded_engine = AnalyticsEngine(storage_dir=tmp_path)
        assert reloaded_engine.data.total_attempts == 2
        assert len(reloaded_engine.data.common_mistakes) == 1
