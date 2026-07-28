"""Prompt Protocol Validator for Scaffold.ai.

Automates validation of AI agent outputs against Learning Mode protocol rules,
generating an objective score and detailed diagnostic breakdown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuleCheck:
    """Diagnostic check for a single protocol rule."""

    rule_number: int
    rule_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    diagnostic: str


@dataclass
class ProtocolValidationResult:
    """Overall result of validating an agent's response text."""

    overall_score: float  # 0.0 to 1.0
    passed: bool
    rule_checks: list[RuleCheck] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "overall_score": self.overall_score,
            "passed": self.passed,
            "rule_checks": [
                {
                    "rule_number": r.rule_number,
                    "rule_name": r.rule_name,
                    "passed": r.passed,
                    "score": r.score,
                    "diagnostic": r.diagnostic,
                }
                for r in self.rule_checks
            ],
            "diagnostics": self.diagnostics,
        }


def validate_protocol(response_text: str) -> ProtocolValidationResult:
    """Validate AI agent output against the Learning Mode protocol rules.

    Parameters
    ----------
    response_text:
        The markdown text returned by the AI agent.

    Returns
    -------
    ProtocolValidationResult
        Detailed diagnostic report and overall compliance score.
    """
    if not response_text or not response_text.strip():
        return ProtocolValidationResult(
            overall_score=0.0,
            passed=False,
            rule_checks=[],
            diagnostics=["Response text is empty."],
        )

    text = response_text.strip()
    checks: list[RuleCheck] = []

    # Rule 1: Goal Explanation Before Code
    code_match = re.search(r"```[a-zA-Z]*\n", text)
    first_code_pos = code_match.start() if code_match else len(text)
    pre_code_text = text[:first_code_pos]

    has_goal_keywords = any(
        kw in pre_code_text.lower()
        for kw in ["goal", "purpose", "aim", "objective", "in this milestone", "blueprint", "first step"]
    )
    r1_pass = len(pre_code_text) > 50 and has_goal_keywords
    checks.append(
        RuleCheck(
            rule_number=1,
            rule_name="Explain Goal First",
            passed=r1_pass,
            score=1.0 if r1_pass else 0.4,
            diagnostic=(
                "Goal and purpose explained before first code block."
                if r1_pass
                else "Missing sufficient explanatory text or goal description before code."
            ),
        )
    )

    # Rule 2: Stay in Scope
    r2_pass = not any(
        kw in text.lower()
        for kw in ["in the next milestone we will build persistence", "jumping ahead to cli"]
    )
    checks.append(
        RuleCheck(
            rule_number=2,
            rule_name="Stay in Scope",
            passed=r2_pass,
            score=1.0 if r2_pass else 0.5,
            diagnostic="Response remains focused on current milestone scope." if r2_pass else "Possible scope drift detected.",
        )
    )

    # Rule 3: Sequential Concepts & Code Blocks
    code_blocks = re.findall(r"```[a-zA-Z]*\n[\s\S]*?\n```", text)
    has_code = len(code_blocks) > 0
    r3_pass = has_code and len(text) > (sum(len(b) for b in code_blocks))
    checks.append(
        RuleCheck(
            rule_number=3,
            rule_name="Sequential Concept Explanation",
            passed=r3_pass,
            score=1.0 if r3_pass else 0.3,
            diagnostic="Code blocks are accompanied by explanatory prose." if r3_pass else "Code blocks lack surrounding explanation.",
        )
    )

    # Rule 4: Trade-off & Alternative Discussion
    tradeoff_keywords = [
        "trade-off",
        "tradeoff",
        "alternative",
        "why",
        "instead of",
        "decided to",
        "chose",
        "rejected",
    ]
    has_tradeoff = any(kw in text.lower() for kw in tradeoff_keywords)
    checks.append(
        RuleCheck(
            rule_number=4,
            rule_name="Explain Trade-offs & Alternatives",
            passed=has_tradeoff,
            score=1.0 if has_tradeoff else 0.2,
            diagnostic="Discussed design trade-offs or alternatives." if has_tradeoff else "Missing trade-off or alternative rationale.",
        )
    )

    # Rule 5: Exactly One Reflective Question
    has_reflection_heading = "Reflective Question" in text or "🤔" in text
    question_count = len(re.findall(r"\?", text))
    r5_pass = has_reflection_heading and question_count >= 1
    checks.append(
        RuleCheck(
            rule_number=5,
            rule_name="Reflective Question & Stop",
            passed=r5_pass,
            score=1.0 if r5_pass else 0.0,
            diagnostic="Contains clearly marked reflective question." if r5_pass else "Missing reflective question heading or question mark.",
        )
    )

    # Rule 6: Milestone Completeness Check
    has_checklist = bool(re.search(r"\[x\]|milestone (check|review|completed|progress)", text.lower()))
    checks.append(
        RuleCheck(
            rule_number=6,
            rule_name="Milestone Completeness",
            passed=has_checklist or r3_pass,
            score=1.0 if (has_checklist or r3_pass) else 0.5,
            diagnostic="Milestone completeness check present." if (has_checklist or r3_pass) else "Missing explicit completeness check.",
        )
    )

    # Calculate overall score
    overall_score = sum(c.score for c in checks) / len(checks)
    overall_pass = overall_score >= 0.75 and r5_pass

    diagnostics = [c.diagnostic for c in checks if not c.passed]
    if not diagnostics:
        diagnostics = ["Response fully adheres to Learning Mode protocol rules."]

    return ProtocolValidationResult(
        overall_score=round(overall_score, 2),
        passed=overall_pass,
        rule_checks=checks,
        diagnostics=diagnostics,
    )
