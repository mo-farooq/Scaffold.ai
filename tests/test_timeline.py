"""Tests for Learning Timeline Engine."""

from __future__ import annotations

from pathlib import Path

from scaffold.timeline import LearningTimeline


class TestLearningTimeline:
    def test_record_concept(self, tmp_path: Path) -> None:
        timeline = LearningTimeline(storage_dir=tmp_path)
        assert len(timeline.data.entries) == 0

        entry = timeline.record_concept(
            milestone_index=0,
            milestone_title="Data Model",
            concept_learned="Dataclasses",
            files_modified=["src/model.py"],
            adrs_referenced=["ADR-001"],
        )
        assert entry.concept_learned == "Dataclasses"
        assert len(timeline.data.entries) == 1

        # Reload from disk
        reloaded = LearningTimeline(storage_dir=tmp_path)
        assert len(reloaded.data.entries) == 1
        assert reloaded.data.entries[0].concept_learned == "Dataclasses"
