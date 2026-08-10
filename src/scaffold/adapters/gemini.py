"""Gemini Adapter for Scaffold.ai.

Wraps the Google GenAI SDK (`google-genai`) to send Learning Mode system prompts
and student messages to Gemini models, returning uniform AgentResponse objects.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from scaffold.adapters.base import AgentAdapter, AgentResponse


class GeminiAdapter(AgentAdapter):
    """Agent adapter for direct Gemini API communication.

    Parameters
    ----------
    api_key:
        Gemini API key. Falls back to GEMINI_API_KEY env var.
    model_name:
        The Gemini model to use (default: 'gemini-3.1-flash-lite').
    temperature:
        Sampling temperature for response generation.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.1-flash-lite",
        temperature: float = 0.7,
    ) -> None:
        load_dotenv()
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self._api_key.strip():
            raise ValueError(
                "GEMINI_API_KEY is missing. Pass api_key or set GEMINI_API_KEY env var."
            )
        self._model_name = model_name
        self._temperature = temperature
        self._client = genai.Client(api_key=self._api_key)

    @property
    def adapter_name(self) -> str:
        return "gemini"

    def send_message(
        self,
        user_message: str,
        system_prompt: str = "",
    ) -> AgentResponse:
        """Send a message to Gemini and return an AgentResponse.

        Parameters
        ----------
        user_message:
            The student/user message to send.
        system_prompt:
            The Learning Mode system prompt to inject as system_instruction.

        Returns
        -------
        AgentResponse
        """
        self._validate_message(user_message)

        config = types.GenerateContentConfig(
            temperature=self._temperature,
        )
        if system_prompt.strip():
            config.system_instruction = system_prompt

        response, elapsed = self._timed_call(
            self._client.models.generate_content,
            model=self._model_name,
            contents=user_message,
            config=config,
        )

        content = response.text or ""

        return AgentResponse(
            content=content,
            model_name=self._model_name,
            latency_seconds=round(elapsed, 3),
            raw_response=response,
            metadata={
                "adapter": "gemini",
                "temperature": self._temperature,
            },
        )
