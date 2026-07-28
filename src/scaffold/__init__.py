"""Scaffold – Learning Mode prompt wrapper & milestone generator."""

from scaffold.generator import generate_milestones
from scaffold.prompt import MilestoneContext, build_prompt

__all__ = ["MilestoneContext", "build_prompt", "generate_milestones"]

