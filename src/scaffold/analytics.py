"""Reflection Analytics Engine for Scaffold.ai.

Tracks student learning metrics, reflection attempts, time spent, evaluation scores,
and common mistakes in `.scaffold/analytics.json` (decoupled from session state).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scaffold.evaluator import EvaluationResult


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class AnalyticsRecord:
    """Record of a single reflection evaluation attempt."""

    timestamp: str
    milestone_index: int
    question: str
    student_answer: str
    passed: bool
    score: float
    feedback: str
    hint: str | None = None
    duration_seconds: float = 0.0


@dataclass
class AnalyticsData:
    """Aggregated learning analytics storage."""

    total_attempts: int = 0
    successful_evaluations: int = 0
    failed_evaluations: int = 0
    total_duration_seconds: float = 0.0
    records: list[AnalyticsRecord] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Calculate overall evaluation pass rate (0.0 to 100.0)."""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_evaluations / self.total_attempts) * 100.0

    def to_dict(self) -> dict[str, Any]:
        """Convert data to JSON-serializable dictionary."""
        return {
            "total_attempts": self.total_attempts,
            "successful_evaluations": self.successful_evaluations,
            "failed_evaluations": self.failed_evaluations,
            "total_duration_seconds": round(self.total_duration_seconds, 2),
            "pass_rate": round(self.pass_rate, 1),
            "records": [asdict(r) for r in self.records],
            "common_mistakes": self.common_mistakes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalyticsData:
        """Construct object from dictionary."""
        raw_records = data.get("records", [])
        records = [
            AnalyticsRecord(
                timestamp=r.get("timestamp", _utc_now_iso()),
                milestone_index=int(r.get("milestone_index", 0)),
                question=str(r.get("question", "")),
                student_answer=str(r.get("student_answer", "")),
                passed=bool(r.get("passed", False)),
                score=float(r.get("score", 0.0)),
                feedback=str(r.get("feedback", "")),
                hint=r.get("hint"),
                duration_seconds=float(r.get("duration_seconds", 0.0)),
            )
            for r in raw_records
        ]
        return cls(
            total_attempts=int(data.get("total_attempts", len(records))),
            successful_evaluations=int(data.get("successful_evaluations", sum(1 for r in records if r.passed))),
            failed_evaluations=int(data.get("failed_evaluations", sum(1 for r in records if not r.passed))),
            total_duration_seconds=float(data.get("total_duration_seconds", 0.0)),
            records=records,
            common_mistakes=list(data.get("common_mistakes", [])),
        )


class AnalyticsEngine:
    """Engine for persisting and analyzing student reflection performance."""

    def __init__(self, storage_dir: str | Path = ".scaffold") -> None:
        self.storage_dir = Path(storage_dir)
        self.filepath = self.storage_dir / "analytics.json"
        self.data = self._load()

    def _load(self) -> AnalyticsData:
        if not self.filepath.exists():
            return AnalyticsData()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return AnalyticsData.from_dict(raw)
        except Exception:
            return AnalyticsData()

    def save(self) -> Path:
        """Persist analytics data to .scaffold/analytics.json."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data.to_dict(), f, indent=2)
        return self.filepath

    def record_attempt(
        self,
        milestone_index: int,
        question: str,
        student_answer: str,
        result: EvaluationResult,
        duration_seconds: float = 0.0,
    ) -> AnalyticsRecord:
        """Record a single evaluation attempt."""
        rec = AnalyticsRecord(
            timestamp=_utc_now_iso(),
            milestone_index=milestone_index,
            question=question,
            student_answer=student_answer,
            passed=result.passed,
            score=result.score,
            feedback=result.feedback,
            hint=result.hint,
            duration_seconds=duration_seconds,
        )

        self.data.records.append(rec)
        self.data.total_attempts += 1
        self.data.total_duration_seconds += max(0.0, duration_seconds)

        if result.passed:
            self.data.successful_evaluations += 1
        else:
            self.data.failed_evaluations += 1
            if result.feedback and result.feedback not in self.data.common_mistakes:
                self.data.common_mistakes.append(result.feedback[:100])

        self.save()
        return rec
