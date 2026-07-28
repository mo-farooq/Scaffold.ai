"""Scaffold – Learning Mode prompt wrapper, milestone generator, and session engine."""

from scaffold.generator import generate_milestones
from scaffold.prompt import MilestoneContext, build_prompt
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

__all__ = [
    "MilestoneContext",
    "Session",
    "SessionState",
    "advance_milestone",
    "build_prompt",
    "generate_milestones",
    "get_current_context",
    "init_session",
    "load_session",
    "reset_session",
    "save_session",
]

