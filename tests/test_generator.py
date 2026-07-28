"""Tests for the Dynamic Milestone Generator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from scaffold.generator import _clean_json_text, generate_milestones


class TestCleanJsonText:
    def test_plain_json_string(self) -> None:
        raw = '["M1", "M2", "M3"]'
        assert _clean_json_text(raw) == raw

    def test_markdown_json_block(self) -> None:
        raw = "```json\n[\"M1\", \"M2\", \"M3\"]\n```"
        assert _clean_json_text(raw) == '["M1", "M2", "M3"]'

    def test_generic_markdown_block(self) -> None:
        raw = "```\n[\"M1\", \"M2\", \"M3\"]\n```"
        assert _clean_json_text(raw) == '["M1", "M2", "M3"]'

    def test_with_surrounding_whitespace(self) -> None:
        raw = "  \n ```json\n[\"M1\", \"M2\", \"M3\"]\n```  \n"
        assert _clean_json_text(raw) == '["M1", "M2", "M3"]'


class TestGeneratorInputValidation:
    def test_empty_description_raises(self) -> None:
        with pytest.raises(ValueError, match="project_description must not be empty"):
            generate_milestones("   ")

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setattr("scaffold.generator.load_dotenv", lambda: None)
        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            generate_milestones("A valid project description")


class TestGeneratorResponseParsing:
    @patch("scaffold.generator.genai.Client")
    def test_successful_mocked_generation(
        self, mock_client_cls: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
        
        # Setup mock client
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '["1. Data Model", "2. Core API", "3. CLI Interface", "4. Persistence"]'
        mock_client.models.generate_content.return_value = mock_response

        res = generate_milestones("Build a Todo App")
        assert len(res) == 4
        assert res[0] == "1. Data Model"
        assert res[3] == "4. Persistence"

    @patch("scaffold.generator.genai.Client")
    def test_invalid_json_raises_valueerror(
        self, mock_client_cls: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
        
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to parse LLM milestone JSON response"):
            generate_milestones("Build a Todo App")

    @patch("scaffold.generator.genai.Client")
    def test_out_of_range_count_raises_valueerror(
        self, mock_client_cls: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
        
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        # Only 2 milestones (minimum required is 3)
        mock_response.text = '["1. Data Model", "2. Core API"]'
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ValueError, match="Expected between 3 and 6 milestones"):
            generate_milestones("Build a Todo App")


@pytest.mark.integration
class TestLiveGeneratorIntegration:
    def test_live_milestone_generation(self) -> None:
        """Live call to Gemini API to test milestone generation end-to-end."""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        if not os.environ.get("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        milestones = generate_milestones("A command-line Todo app in Python")
        assert isinstance(milestones, list)
        assert 3 <= len(milestones) <= 6
        for m in milestones:
            assert isinstance(m, str)
            assert len(m) > 3
