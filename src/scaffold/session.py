"""Session State Machine & Local Storage for Scaffold.ai.

Manages student progress, milestone context generation, and state transitions
persisted inside a local `.scaffold/session.json` file.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import os
from pathlib import Path
from typing import Any

from scaffold.prompt import MilestoneContext


class SessionState(str, Enum):
    """The current state of a student's Learning Mode session."""

    UNINITIALIZED = "UNINITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_REFLECTION = "AWAITING_REFLECTION"
    COMPLETED = "COMPLETED"


def _utc_now_iso() -> str:
    """Get current UTC timestamp as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    """Represents an active Scaffold.ai learning session."""

    project_description: str
    milestones: list[str]
    current_index: int = 0
    state: SessionState = SessionState.IN_PROGRESS
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.project_description or not self.project_description.strip():
            raise ValueError("project_description must not be empty")
        if not self.milestones:
            raise ValueError("milestones must contain at least one item")
        
        # Ensure state is a SessionState enum instance
        if isinstance(self.state, str):
            try:
                self.state = SessionState(self.state)
            except ValueError:
                self.state = SessionState.IN_PROGRESS

        # Validate current index range
        if self.current_index < 0:
            raise IndexError("current_index must not be negative")
        
        if self.current_index >= len(self.milestones):
            self.state = SessionState.COMPLETED

    @property
    def current_milestone(self) -> str:
        """Get title of the current milestone."""
        if self.current_index < len(self.milestones):
            return self.milestones[self.current_index]
        return self.milestones[-1]

    @property
    def is_completed(self) -> bool:
        """True if all milestones have been finished."""
        return self.state == SessionState.COMPLETED or self.current_index >= len(self.milestones)

    @property
    def progress_percentage(self) -> float:
        """Get completion percentage (0.0 to 100.0)."""
        if not self.milestones:
            return 0.0
        if self.is_completed:
            return 100.0
        return (self.current_index / len(self.milestones)) * 100.0

    def to_dict(self) -> dict[str, Any]:
        """Convert session object to serializable dictionary."""
        data = asdict(self)
        data["state"] = self.state.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        """Construct Session object from dictionary data."""
        state_str = data.get("state", SessionState.IN_PROGRESS.value)
        try:
            state_enum = SessionState(state_str)
        except ValueError:
            state_enum = SessionState.IN_PROGRESS

        return cls(
            project_description=data["project_description"],
            milestones=list(data["milestones"]),
            current_index=int(data.get("current_index", 0)),
            state=state_enum,
            created_at=data.get("created_at", _utc_now_iso()),
            updated_at=data.get("updated_at", _utc_now_iso()),
            history=list(data.get("history", [])),
        )


def _get_session_path(session_dir: str | Path = ".scaffold") -> Path:
    """Get absolute path to session.json file."""
    path = Path(session_dir)
    return path / "session.json"


def init_session(
    project_description: str,
    milestones: list[str],
    session_dir: str | Path = ".scaffold",
) -> Session:
    """Initialize and persist a new Scaffold.ai learning session.

    Parameters
    ----------
    project_description:
        The project description text.
    milestones:
        List of milestone strings.
    session_dir:
        Directory where session.json is stored (default: '.scaffold').

    Returns
    -------
    Session
        The newly created and saved Session object.
    """
    session = Session(
        project_description=project_description.strip(),
        milestones=milestones,
        current_index=0,
        state=SessionState.IN_PROGRESS,
    )
    save_session(session, session_dir=session_dir)
    return session


def load_session(session_dir: str | Path = ".scaffold") -> Session:
    """Load active session from .scaffold/session.json.

    Parameters
    ----------
    session_dir:
        Directory containing session.json.

    Returns
    -------
    Session
        The loaded Session instance.

    Raises
    ------
    FileNotFoundError
        If session.json does not exist.
    ValueError
        If session.json is invalid or corrupted.
    """
    filepath = _get_session_path(session_dir)
    if not filepath.exists():
        raise FileNotFoundError(
            f"No active session found at {filepath}. Run 'scaffold init' first."
        )

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Session.from_dict(data)
    except Exception as err:
        raise ValueError(f"Corrupted or invalid session file at {filepath}: {err}") from err


def save_session(session: Session, session_dir: str | Path = ".scaffold") -> Path:
    """Save session state to .scaffold/session.json.

    Parameters
    ----------
    session:
        The Session object to persist.
    session_dir:
        Target directory for session storage.

    Returns
    -------
    Path
        Path to saved session.json file.
    """
    dir_path = Path(session_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    filepath = dir_path / "session.json"
    session.updated_at = _utc_now_iso()
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session.to_dict(), f, indent=2)

    return filepath


def get_current_context(session: Session) -> MilestoneContext:
    """Convert a Session object into a MilestoneContext for prompt building.

    Parameters
    ----------
    session:
        Active Session instance.

    Returns
    -------
    MilestoneContext
        MilestoneContext object ready for build_prompt().
    """
    # Clamp index if completed
    safe_index = min(session.current_index, len(session.milestones) - 1)
    return MilestoneContext(
        project_description=session.project_description,
        milestones=session.milestones,
        current_index=safe_index,
    )


def advance_milestone(session: Session, session_dir: str | Path = ".scaffold") -> Session:
    """Advance session to the next milestone.

    If current_index reaches the end of milestones, sets state to COMPLETED.

    Parameters
    ----------
    session:
        The active Session instance.
    session_dir:
        Directory containing session.json.

    Returns
    -------
    Session
        The updated Session object.
    """
    if session.is_completed:
        session.state = SessionState.COMPLETED
        save_session(session, session_dir=session_dir)
        return session

    session.current_index += 1
    if session.current_index >= len(session.milestones):
        session.state = SessionState.COMPLETED
    else:
        session.state = SessionState.IN_PROGRESS

    save_session(session, session_dir=session_dir)
    return session


def reset_session(session_dir: str | Path = ".scaffold") -> bool:
    """Delete session.json and remove session directory if empty.

    Parameters
    ----------
    session_dir:
        Directory containing session.json.

    Returns
    -------
    bool
        True if session file was removed, False if no session existed.
    """
    filepath = _get_session_path(session_dir)
    if not filepath.exists():
        return False

    os.remove(filepath)
    # Remove directory if empty
    dir_path = Path(session_dir)
    try:
        if dir_path.exists() and not any(dir_path.iterdir()):
            dir_path.rmdir()
    except OSError:
        pass

    return True
