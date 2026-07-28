"""Learning Timeline Engine for Scaffold.ai.

Records concepts learned, files modified, architectural decisions referenced,
reflection outcomes, and milestone history in `.scaffold/timeline.json`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class TimelineEntry:
    """A single event or concept entry in the student's learning timeline."""

    timestamp: str
    milestone_index: int
    milestone_title: str
    concept_learned: str
    files_modified: list[str] = field(default_factory=list)
    adrs_referenced: list[str] = field(default_factory=list)
    reflection_outcome: str = "PASSED"  # "PASSED" or "RETRY"
    notes: str = ""


@dataclass
class TimelineData:
    """Container for the student's learning timeline."""

    project_description: str = ""
    entries: list[TimelineEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert timeline to JSON-serializable dictionary."""
        return {
            "project_description": self.project_description,
            "total_concepts_learned": len(self.entries),
            "entries": [asdict(e) for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimelineData:
        """Construct object from dictionary."""
        raw_entries = data.get("entries", [])
        entries = [
            TimelineEntry(
                timestamp=e.get("timestamp", _utc_now_iso()),
                milestone_index=int(e.get("milestone_index", 0)),
                milestone_title=str(e.get("milestone_title", "")),
                concept_learned=str(e.get("concept_learned", "")),
                files_modified=list(e.get("files_modified", [])),
                adrs_referenced=list(e.get("adrs_referenced", [])),
                reflection_outcome=str(e.get("reflection_outcome", "PASSED")),
                notes=str(e.get("notes", "")),
            )
            for e in raw_entries
        ]
        return cls(
            project_description=str(data.get("project_description", "")),
            entries=entries,
        )


class LearningTimeline:
    """Engine for recording and retrieving student learning timeline history."""

    def __init__(self, storage_dir: str | Path = ".scaffold") -> None:
        self.storage_dir = Path(storage_dir)
        self.filepath = self.storage_dir / "timeline.json"
        self.data = self._load()

    def _load(self) -> TimelineData:
        if not self.filepath.exists():
            return TimelineData()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return TimelineData.from_dict(raw)
        except Exception:
            return TimelineData()

    def save(self) -> Path:
        """Save timeline data to .scaffold/timeline.json."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data.to_dict(), f, indent=2)
        return self.filepath

    def record_concept(
        self,
        milestone_index: int,
        milestone_title: str,
        concept_learned: str,
        files_modified: list[str] | None = None,
        adrs_referenced: list[str] | None = None,
        reflection_outcome: str = "PASSED",
        notes: str = "",
    ) -> TimelineEntry:
        """Record a completed learning concept in the timeline."""
        entry = TimelineEntry(
            timestamp=_utc_now_iso(),
            milestone_index=milestone_index,
            milestone_title=milestone_title,
            concept_learned=concept_learned,
            files_modified=files_modified or [],
            adrs_referenced=adrs_referenced or [],
            reflection_outcome=reflection_outcome,
            notes=notes,
        )
        self.data.entries.append(entry)
        self.save()
        return entry
