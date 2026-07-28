"""Reflection Evaluator Engine for Scaffold.ai.

Uses an LLM (Gemini API) to assess student responses to reflective questions,
evaluating conceptual understanding and providing constructive hints when needed.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


def _clean_json_text(text: str) -> str:
    """Strip markdown code fence wrappers from raw LLM output text."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


@dataclass
class EvaluationResult:
    """The result of evaluating a student's answer to a reflective question."""

    passed: bool
    score: float  # 0.0 to 1.0
    feedback: str
    hint: str | None = None
    suggested_action: str = "ADVANCE"  # "ADVANCE" or "RETRY"

    def __post_init__(self) -> None:
        # Normalize score bounds
        self.score = max(0.0, min(1.0, float(self.score)))
        if self.passed:
            self.suggested_action = "ADVANCE"
        else:
            self.suggested_action = "RETRY"

    def to_dict(self) -> dict[str, Any]:
        """Convert result object to dictionary."""
        return {
            "passed": self.passed,
            "score": self.score,
            "feedback": self.feedback,
            "hint": self.hint,
            "suggested_action": self.suggested_action,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationResult:
        """Construct EvaluationResult object from dictionary."""
        return cls(
            passed=bool(data.get("passed", False)),
            score=float(data.get("score", 0.0)),
            feedback=str(data.get("feedback", "")),
            hint=data.get("hint"),
            suggested_action=str(data.get("suggested_action", "RETRY")),
        )


def evaluate_answer(
    student_answer: str,
    question: str,
    milestone_title: str = "",
    project_description: str = "",
    api_key: str | None = None,
    model_name: str = "gemini-3.1-flash-lite",
) -> EvaluationResult:
    """Evaluate a student's response to a reflective learning question.

    Parameters
    ----------
    student_answer:
        The text response provided by the student.
    question:
        The reflective question issued by the AI tutor.
    milestone_title:
        Context title of the active milestone (optional).
    project_description:
        Context description of the overall project (optional).
    api_key:
        Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
    model_name:
        The Gemini model to call (default: 'gemini-3.1-flash-lite').

    Returns
    -------
    EvaluationResult
        Evaluation outcome containing passed status, score, feedback, and hint.

    Raises
    ------
    ValueError
        If student_answer or question is empty, or API key is missing.
    """
    if not student_answer or not student_answer.strip():
        raise ValueError("student_answer must not be empty")
    if not question or not question.strip():
        raise ValueError("question must not be empty")

    load_dotenv()
    resolved_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY")
    if not resolved_key or not resolved_key.strip():
        raise ValueError(
            "GEMINI_API_KEY is missing. Pass api_key or set GEMINI_API_KEY environment variable."
        )

    system_instruction = (
        "You are an expert computer science educator and supportive tutor. "
        "Your task is to evaluate a student's answer to a reflective learning question.\n\n"
        "Evaluation Principles:\n"
        "1. Focus on CONCEPTUAL UNDERSTANDING, trade-off awareness, and reasoning — NOT verbatim phrasing or exact code syntax.\n"
        "2. If the student demonstrates a correct grasp of the underlying principle or trade-off, set passed = true and score between 0.8 and 1.0.\n"
        "3. If the student's answer is wrong, confused, or demonstrates a fundamental misunderstanding, set passed = false and score between 0.0 and 0.5.\n"
        "4. Provide encouraging, constructive feedback explaining why their reasoning is sound or where it fell short.\n"
        "5. If passed = false, provide a targeted 'hint' that guides their thinking toward the correct answer WITHOUT giving away direct code solutions.\n\n"
        "Output Format:\n"
        "You MUST respond ONLY with a valid JSON object matching this schema:\n"
        "{\n"
        '  "passed": true | false,\n'
        '  "score": 0.85,\n'
        '  "feedback": "Great explanation! You correctly identified...",\n'
        '  "hint": null or "Consider what happens when...",\n'
        '  "suggested_action": "ADVANCE" or "RETRY"\n'
        "}"
    )

    user_prompt = (
        f"Project Context: {project_description.strip() or 'N/A'}\n"
        f"Milestone Context: {milestone_title.strip() or 'N/A'}\n\n"
        f"Reflective Question:\n\"{question.strip()}\"\n\n"
        f"Student's Answer:\n\"{student_answer.strip()}\"\n\n"
        f"Evaluate the student's answer now."
    )

    client = genai.Client(api_key=resolved_key)

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        response_mime_type="application/json",
        response_schema=EvaluationResult,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=config,
    )

    raw_text = response.text or ""
    cleaned_text = _clean_json_text(raw_text)

    try:
        data = json.loads(cleaned_text)
        return EvaluationResult.from_dict(data)
    except Exception as err:
        raise ValueError(f"Failed to parse LLM evaluation JSON response: {err}") from err
