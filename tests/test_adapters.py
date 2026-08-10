"""Tests for Scaffold.ai Agent Adapter Layer.

Covers: AgentResponse model, AgentAdapter contract validation, factory registry,
mocked adapter calls, and live Gemini integration.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scaffold.adapters import (
    AgentAdapter,
    AgentResponse,
    ClaudeAdapter,
    GeminiAdapter,
    get_adapter,
    list_available_adapters,
)
from scaffold.adapters.base import AgentAdapter as BaseAgentAdapter


# ─── AgentResponse Model ─────────────────────────────────────────────────

class TestAgentResponse:
    def test_default_values(self) -> None:
        resp = AgentResponse(content="Hello world")
        assert resp.content == "Hello world"
        assert resp.model_name == ""
        assert resp.latency_seconds == 0.0
        assert resp.raw_response is None
        assert resp.metadata == {}

    def test_full_construction(self) -> None:
        resp = AgentResponse(
            content="Test response",
            model_name="gemini-3.1-flash-lite",
            latency_seconds=1.234,
            raw_response={"raw": True},
            metadata={"adapter": "gemini"},
        )
        assert resp.model_name == "gemini-3.1-flash-lite"
        assert resp.latency_seconds == 1.234
        assert resp.metadata["adapter"] == "gemini"


# ─── AgentAdapter Contract ────────────────────────────────────────────────

class TestAgentAdapterContract:
    def test_adapter_is_abstract(self) -> None:
        """AgentAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgentAdapter()  # type: ignore[abstract]

    def test_validate_message_rejects_empty(self) -> None:
        """_validate_message should raise on empty strings."""

        class StubAdapter(BaseAgentAdapter):
            @property
            def adapter_name(self) -> str:
                return "stub"

            def send_message(self, user_message: str, system_prompt: str = "") -> AgentResponse:
                self._validate_message(user_message)
                return AgentResponse(content="ok")

        adapter = StubAdapter()
        with pytest.raises(ValueError, match="user_message must not be empty"):
            adapter.send_message("")
        with pytest.raises(ValueError, match="user_message must not be empty"):
            adapter.send_message("   ")


# ─── Factory Registry ─────────────────────────────────────────────────────

class TestAdapterFactory:
    def test_list_available_adapters(self) -> None:
        adapters = list_available_adapters()
        assert "gemini" in adapters
        assert "claude" in adapters
        assert adapters == sorted(adapters)

    def test_get_adapter_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown adapter"):
            get_adapter("nonexistent")

    def test_get_adapter_gemini(self) -> None:
        adapter = get_adapter("gemini", api_key="test-key-123")
        assert isinstance(adapter, GeminiAdapter)
        assert adapter.adapter_name == "gemini"

    def test_get_adapter_claude(self) -> None:
        adapter = get_adapter("claude")
        assert isinstance(adapter, ClaudeAdapter)
        assert adapter.adapter_name == "claude"

    def test_get_adapter_case_insensitive(self) -> None:
        adapter = get_adapter("GEMINI", api_key="test-key-123")
        assert isinstance(adapter, GeminiAdapter)


# ─── GeminiAdapter ─────────────────────────────────────────────────────────

class TestGeminiAdapter:
    def test_missing_api_key_raises(self) -> None:
        with patch("scaffold.adapters.gemini.load_dotenv"):
            with patch.dict("os.environ", {}, clear=True):
                with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
                    GeminiAdapter(api_key="")

    def test_empty_message_raises(self) -> None:
        adapter = GeminiAdapter(api_key="test-key")
        with pytest.raises(ValueError, match="user_message must not be empty"):
            adapter.send_message("")

    @patch("scaffold.adapters.gemini.genai.Client")
    def test_mocked_send_message(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Here is milestone 1 explanation..."
        mock_client.models.generate_content.return_value = mock_response

        adapter = GeminiAdapter(api_key="test-key")
        result = adapter.send_message("Start the first milestone", system_prompt="You are a tutor.")

        assert isinstance(result, AgentResponse)
        assert result.content == "Here is milestone 1 explanation..."
        assert result.model_name == "gemini-3.1-flash-lite"
        assert result.latency_seconds >= 0.0
        assert result.metadata["adapter"] == "gemini"


# ─── ClaudeAdapter ─────────────────────────────────────────────────────────

class TestClaudeAdapter:
    def test_adapter_name(self) -> None:
        adapter = ClaudeAdapter()
        assert adapter.adapter_name == "claude"

    def test_empty_message_raises(self) -> None:
        adapter = ClaudeAdapter()
        with pytest.raises(ValueError, match="user_message must not be empty"):
            adapter.send_message("")

    @patch("scaffold.adapters.claude.shutil.which")
    def test_missing_cli_raises_runtime_error(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        adapter = ClaudeAdapter(cli_path=None)
        adapter._cli_path = None  # Force re-check
        with pytest.raises(RuntimeError, match="not found in PATH"):
            adapter.send_message("Hello")

    @patch("scaffold.adapters.claude.subprocess.run")
    @patch("scaffold.adapters.claude.shutil.which")
    def test_mocked_successful_call(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_which.return_value = "/usr/local/bin/claude"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Welcome! Let's start with the data model...",
            stderr="",
        )

        adapter = ClaudeAdapter(cli_path="/usr/local/bin/claude")
        result = adapter.send_message("Start milestone 1", system_prompt="You are a tutor.")

        assert isinstance(result, AgentResponse)
        assert result.content == "Welcome! Let's start with the data model..."
        assert result.model_name == "claude-code-cli"
        assert result.metadata["adapter"] == "claude"

    @patch("scaffold.adapters.claude.subprocess.run")
    @patch("scaffold.adapters.claude.shutil.which")
    def test_nonzero_exit_raises_runtime_error(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_which.return_value = "/usr/local/bin/claude"
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Authentication failed",
        )

        adapter = ClaudeAdapter(cli_path="/usr/local/bin/claude")
        with pytest.raises(RuntimeError, match="exited with code 1"):
            adapter.send_message("Hello")


# ─── Live Gemini Integration ──────────────────────────────────────────────

class TestLiveGeminiAdapterIntegration:
    @pytest.mark.live
    def test_live_gemini_send_message(self) -> None:
        adapter = GeminiAdapter()
        response = adapter.send_message(
            user_message="What is a Python dataclass in one sentence?",
            system_prompt="You are a helpful coding tutor. Answer concisely.",
        )
        assert isinstance(response, AgentResponse)
        assert len(response.content) > 10
        assert response.latency_seconds > 0.0
        assert response.model_name == "gemini-3.1-flash-lite"
