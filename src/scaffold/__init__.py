"""Scaffold – Learning Mode prompt wrapper, milestone generator, session engine, evaluator, validator, analytics, timeline, and agent adapters."""

from scaffold.adapters import (
    AgentAdapter,
    AgentResponse,
    ClaudeAdapter,
    GeminiAdapter,
    get_adapter,
    list_available_adapters,
)
from scaffold.analytics import AnalyticsData, AnalyticsEngine, AnalyticsRecord
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
from scaffold.timeline import LearningTimeline, TimelineData, TimelineEntry
from scaffold.validator import ProtocolValidationResult, RuleCheck, validate_protocol

__all__ = [
    "AgentAdapter",
    "AgentResponse",
    "AnalyticsData",
    "AnalyticsEngine",
    "AnalyticsRecord",
    "ClaudeAdapter",
    "EvaluationResult",
    "GeminiAdapter",
    "LearningTimeline",
    "MilestoneContext",
    "ProtocolValidationResult",
    "RuleCheck",
    "Session",
    "SessionState",
    "TimelineData",
    "TimelineEntry",
    "advance_milestone",
    "build_prompt",
    "evaluate_answer",
    "generate_milestones",
    "get_adapter",
    "get_current_context",
    "init_session",
    "list_available_adapters",
    "load_session",
    "reset_session",
    "save_session",
    "validate_protocol",
]


