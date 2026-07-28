"""Prompt wrapper for Learning Mode.

Builds a structured system prompt that tells an AI coding agent (e.g. Claude
Code) to follow the Learning Mode protocol for a single milestone.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MilestoneContext:
    """Everything the prompt wrapper needs to know about where the student is."""

    project_description: str
    milestones: list[str]
    current_index: int  # 0-based

    def __post_init__(self) -> None:
        if not self.project_description.strip():
            raise ValueError("project_description must not be empty")
        if not self.milestones:
            raise ValueError("milestones must contain at least one entry")
        if not 0 <= self.current_index < len(self.milestones):
            raise IndexError(
                f"current_index {self.current_index} out of range for "
                f"{len(self.milestones)} milestones"
            )

    # ── Convenience properties ──────────────────────────────────────────

    @property
    def current_milestone(self) -> str:
        return self.milestones[self.current_index]

    @property
    def completed_milestones(self) -> list[str]:
        return self.milestones[: self.current_index]

    @property
    def upcoming_milestones(self) -> list[str]:
        return self.milestones[self.current_index + 1 :]

    @property
    def is_first(self) -> bool:
        return self.current_index == 0

    @property
    def is_last(self) -> bool:
        return self.current_index == len(self.milestones) - 1

    @property
    def progress_label(self) -> str:
        return f"Milestone {self.current_index + 1} of {len(self.milestones)}"


# ── Prompt sections ─────────────────────────────────────────────────────


def _section(heading: str, body: str) -> str:
    """Wrap *body* under a markdown heading."""
    return f"## {heading}\n\n{body}"


def _build_role_section() -> str:
    return _section(
        "Role",
        (
            "You are a patient coding tutor. Your primary goal is to help the "
            "student *understand* what they are building and why — not to "
            "finish the project as fast as possible."
        ),
    )


def _build_project_section(ctx: MilestoneContext) -> str:
    return _section("Project Overview", ctx.project_description)


def _build_milestone_section(ctx: MilestoneContext) -> str:
    lines: list[str] = []

    # Show the full roadmap with the current milestone highlighted.
    lines.append("### Roadmap\n")
    for i, m in enumerate(ctx.milestones):
        if i < ctx.current_index:
            marker = "✅"
        elif i == ctx.current_index:
            marker = "👉"
        else:
            marker = "⬜"
        lines.append(f"{marker} {i + 1}. {m}")

    lines.append("")
    lines.append(
        f"**Current milestone ({ctx.progress_label}):** {ctx.current_milestone}"
    )

    if ctx.completed_milestones:
        completed = ", ".join(
            f'"{m}"' for m in ctx.completed_milestones
        )
        lines.append(
            f"\nThe student has already completed: {completed}. "
            "You may reference that work but must not modify it."
        )

    return _section("Milestone", "\n".join(lines))


def _build_protocol_section() -> str:
    rules = [
        (
            "Explain first",
            "Begin by explaining the *goal* of this milestone in plain "
            "language. What will the student be able to do once it is done? "
            "Why does it matter in the context of the larger project?",
        ),
        (
            "Stay in scope",
            "Implement ONLY the current milestone. Do not add code, "
            "configuration, or abstractions that belong to a future "
            "milestone. If the student asks about something ahead, "
            "acknowledge it briefly but redirect to the current milestone.",
        ),
        (
            "One concept at a time",
            "When the milestone requires building multiple functions or features "
            "(e.g., all 4 CRUD operations: add, list, update, delete), walk "
            "through them in sequential step-by-step code blocks with "
            "explanations between them. Do not dump all code at once, but do "
            "cover all required items for this milestone.",
        ),
        (
            "Explain trade-offs",
            "For each meaningful decision, explain the reasoning behind the "
            "chosen approach. Include at least one alternative you considered "
            "and why you rejected it.",
        ),
        (
            "End with reflection",
            "Before concluding, re-read the current milestone description and "
            "confirm every distinct part of it (e.g., every function or component "
            "mentioned) has been fully implemented in code. Do not leave any feature "
            "of the current milestone unbuilt. Once all parts of this milestone are complete, "
            "end your response with exactly ONE reflective question for the "
            "student. Then STOP — do not continue to the next milestone.",
        ),
    ]

    body_lines = []
    for i, (title, detail) in enumerate(rules, 1):
        body_lines.append(f"{i}. **{title}:** {detail}")

    return _section("Protocol — Follow These Rules Strictly", "\n".join(body_lines))


def _build_formatting_section() -> str:
    return _section(
        "Formatting",
        (
            "- Use fenced code blocks with the correct language tag.\n"
            "- Keep explanations concise but thorough.\n"
            "- Use analogies when introducing unfamiliar concepts.\n"
            "- Mark the reflective question clearly with the heading "
            '"### 🤔 Reflective Question".'
        ),
    )


# ── Public API ───────────────────────────────────────────────────────────


def build_prompt(ctx: MilestoneContext) -> str:
    """Build the full Learning Mode system prompt for the given context.

    Parameters
    ----------
    ctx:
        A :class:`MilestoneContext` describing the project, milestones,
        and current position.

    Returns
    -------
    str
        A multi-section markdown prompt ready to be used as a system
        prompt (or prepended to the user message) for an AI coding agent.
    """
    sections = [
        "# Learning Mode — System Prompt",
        _build_role_section(),
        _build_project_section(ctx),
        _build_milestone_section(ctx),
        _build_protocol_section(),
        _build_formatting_section(),
    ]
    return "\n\n---\n\n".join(sections) + "\n"
