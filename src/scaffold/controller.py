"""Scaffold Controller — UI-agnostic business logic orchestrator.

Wires together all engine components (generator, session, prompt, adapters,
evaluator, analytics, timeline) into a single controller that any UI layer
(TUI, web, desktop) can call without knowing engine internals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scaffold.adapters import AgentResponse, get_adapter, list_available_adapters
from scaffold.analytics import AnalyticsData, AnalyticsEngine
from scaffold.evaluator import EvaluationResult, evaluate_answer
from scaffold.generator import generate_milestones
from scaffold.prompt import build_prompt
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
from scaffold.timeline import LearningTimeline, TimelineData
from scaffold.validator import ProtocolValidationResult, validate_protocol


class ScaffoldController:
    """UI-agnostic controller for the Scaffold.ai learning workflow.

    This class owns all business logic and state transitions. UI layers
    (Textual TUI, future web UI, etc.) should call these methods and
    render the results — never interact with engines directly.

    Parameters
    ----------
    project_dir:
        Directory for `.scaffold/` session, analytics, and timeline storage.
        Defaults to the current working directory.
    adapter_name:
        Which AI agent adapter to use ('gemini' or 'claude').
    adapter_kwargs:
        Extra keyword arguments forwarded to the adapter constructor.
    """

    def __init__(
        self,
        project_dir: str | Path = ".",
        adapter_name: str = "gemini",
        adapter_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._project_dir = Path(project_dir)
        self._scaffold_dir = self._project_dir / ".scaffold"
        self._adapter_name = adapter_name
        self._adapter_kwargs = adapter_kwargs or {}
        self._session: Session | None = None
        self._analytics: AnalyticsEngine | None = None
        self._timeline: LearningTimeline | None = None

    # ── Properties ────────────────────────────────────────────────────

    @property
    def session(self) -> Session | None:
        """Current active session, or None if no project is loaded."""
        return self._session

    @property
    def has_existing_session(self) -> bool:
        """Check if a saved session exists on disk."""
        return (self._scaffold_dir / "session.json").exists()

    @property
    def is_awaiting_reflection(self) -> bool:
        """Check if the session is waiting for a student reflection answer."""
        if self._session is None:
            return False
        return self._session.state == SessionState.AWAITING_REFLECTION

    @property
    def is_completed(self) -> bool:
        """Check if the session has completed all milestones."""
        if self._session is None:
            return False
        return self._session.state == SessionState.COMPLETED

    @property
    def available_adapters(self) -> list[str]:
        """Return list of registered adapter names."""
        return list_available_adapters()

    # ── Project Lifecycle ─────────────────────────────────────────────

    def init_project(self, description: str) -> Session:
        """Generate milestones for a project idea and initialize a session.

        Parameters
        ----------
        description:
            The student's project idea description.

        Returns
        -------
        Session
            The newly created session object.
        """
        milestones = generate_milestones(description)
        self._session = init_session(
            project_description=description,
            milestones=milestones,
            session_dir=str(self._scaffold_dir),
        )
        self._analytics = AnalyticsEngine(storage_dir=self._scaffold_dir)
        self._timeline = LearningTimeline(storage_dir=self._scaffold_dir)
        return self._session

    def resume_project(self) -> Session:
        """Load an existing session from disk.

        Returns
        -------
        Session

        Raises
        ------
        FileNotFoundError
            If no saved session exists.
        """
        self._session = load_session(session_dir=str(self._scaffold_dir))
        self._analytics = AnalyticsEngine(storage_dir=self._scaffold_dir)
        self._timeline = LearningTimeline(storage_dir=self._scaffold_dir)
        return self._session

    def reset_project(self) -> None:
        """Delete the current session and all associated data."""
        reset_session(session_dir=str(self._scaffold_dir))
        self._session = None

    # ── Learning Session ──────────────────────────────────────────────

    def send_message(self, user_message: str) -> AgentResponse:
        """Send a message to the AI agent with the Learning Mode system prompt.

        Parameters
        ----------
        user_message:
            The student's message or question.

        Returns
        -------
        AgentResponse

        Raises
        ------
        RuntimeError
            If no session is active.
        """
        if self._session is None:
            raise RuntimeError("No active session. Call init_project() or resume_project() first.")

        ctx = get_current_context(self._session)
        system_prompt = build_prompt(ctx)

        adapter = get_adapter(self._adapter_name, **self._adapter_kwargs)
        response = adapter.send_message(
            user_message=user_message,
            system_prompt=system_prompt,
        )

        # Validate protocol compliance
        validation = validate_protocol(response.content)
        response.metadata["protocol_score"] = validation.overall_score
        response.metadata["protocol_passed"] = validation.passed

        # If the response contains a reflective question, transition state
        if validation.passed and "?" in response.content[-500:]:
            self._session.state = SessionState.AWAITING_REFLECTION
            save_session(self._session, session_dir=str(self._scaffold_dir))

        return response

    def submit_answer(self, answer: str) -> EvaluationResult:
        """Submit a student's reflection answer for evaluation.

        Parameters
        ----------
        answer:
            The student's response to the reflective question.

        Returns
        -------
        EvaluationResult

        Raises
        ------
        RuntimeError
            If no session is active.
        """
        if self._session is None:
            raise RuntimeError("No active session.")

        result = evaluate_answer(
            student_answer=answer,
            question="(reflection question from last AI response)",
            milestone_title=self._session.current_milestone,
            project_description=self._session.project_description,
        )

        # Record in analytics
        if self._analytics:
            self._analytics.record_attempt(
                milestone_index=self._session.current_index,
                question="(reflection)",
                student_answer=answer,
                result=result,
            )

        if result.passed:
            # Record concept in timeline
            if self._timeline:
                self._timeline.record_concept(
                    milestone_index=self._session.current_index,
                    milestone_title=self._session.current_milestone,
                    concept_learned=f"Completed: {self._session.current_milestone}",
                    reflection_outcome="PASSED",
                )

            # Advance to next milestone
            self._session = advance_milestone(
                self._session,
                session_dir=str(self._scaffold_dir),
            )
        else:
            # Stay on current milestone, transition back to in-progress
            self._session.state = SessionState.IN_PROGRESS
            save_session(self._session, session_dir=str(self._scaffold_dir))

        return result

    # ── Status & Analytics ────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Get a summary of the current session status.

        Returns
        -------
        dict
            Session state, progress, milestone list, and analytics.
        """
        if self._session is None:
            return {"active": False}

        analytics_data = self._analytics.data if self._analytics else AnalyticsData()

        return {
            "active": True,
            "project_description": self._session.project_description,
            "state": self._session.state.value,
            "current_index": self._session.current_index,
            "current_milestone": self._session.current_milestone,
            "total_milestones": len(self._session.milestones),
            "progress_percentage": self._session.progress_percentage,
            "milestones": self._session.milestones,
            "total_attempts": analytics_data.total_attempts,
            "pass_rate": analytics_data.pass_rate,
            "adapter": self._adapter_name,
        }

    def get_analytics(self) -> AnalyticsData:
        """Get analytics data for the current project."""
        if self._analytics:
            return self._analytics.data
        return AnalyticsData()

    def get_timeline(self) -> TimelineData:
        """Get learning timeline data for the current project."""
        if self._timeline:
            return self._timeline.data
        from scaffold.timeline import TimelineData

        return TimelineData()
