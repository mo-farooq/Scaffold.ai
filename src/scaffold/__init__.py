"""Scaffold – Learning Mode prompt wrapper, milestone generator, session engine, and evaluator."""

from scaffold.evaluator import EvaluationResult, evaluate_answer
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
    "EvaluationResult",
    "MilestoneContext",
    "Session",
    "SessionState",
    "advance_milestone",
    "build_prompt",
    "evaluate_answer",
    "generate_milestones",
    "get_current_context",
    "init_session",
    "load_session",
    "reset_session",
    "save_session",
]

