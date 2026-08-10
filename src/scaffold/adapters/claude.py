"""Claude Code CLI Adapter for Scaffold.ai.

Wraps Anthropic's `claude` command-line tool via subprocess to send
Learning Mode system prompts and student messages, returning uniform
AgentResponse objects.
"""

from __future__ import annotations

import shutil
import subprocess

from scaffold.adapters.base import AgentAdapter, AgentResponse


class ClaudeAdapter(AgentAdapter):
    """Agent adapter for Claude Code CLI (`claude`) subprocess execution.

    Parameters
    ----------
    cli_path:
        Absolute path to the `claude` binary. If None, searches PATH.
    timeout_seconds:
        Maximum wall-clock time for the subprocess (default: 120s).
    """

    def __init__(
        self,
        cli_path: str | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        self._cli_path = cli_path or shutil.which("claude")
        self._timeout = timeout_seconds

    @property
    def adapter_name(self) -> str:
        return "claude"

    def _ensure_cli_available(self) -> str:
        """Verify that the claude CLI binary is accessible.

        Returns
        -------
        str
            The resolved path to the claude binary.

        Raises
        ------
        RuntimeError
            If claude is not found in PATH.
        """
        if self._cli_path and shutil.which(self._cli_path):
            return self._cli_path
        # Re-check PATH in case it was installed after init
        resolved = shutil.which("claude")
        if resolved:
            self._cli_path = resolved
            return resolved
        raise RuntimeError(
            "Claude Code CLI ('claude') not found in PATH. "
            "Install it with: npm install -g @anthropic-ai/claude-code\n"
            "See: https://docs.anthropic.com/en/docs/claude-code"
        )

    def send_message(
        self,
        user_message: str,
        system_prompt: str = "",
    ) -> AgentResponse:
        """Send a message to Claude Code CLI and return an AgentResponse.

        Executes `claude --print --system-prompt <system_prompt> <user_message>`
        as a subprocess, capturing stdout as the response content.

        Parameters
        ----------
        user_message:
            The student/user message to send.
        system_prompt:
            The Learning Mode system prompt to inject via --system-prompt flag.

        Returns
        -------
        AgentResponse

        Raises
        ------
        RuntimeError
            If the claude CLI is not installed or the subprocess fails.
        """
        self._validate_message(user_message)
        cli_binary = self._ensure_cli_available()

        cmd = [cli_binary, "--print"]
        if system_prompt.strip():
            cmd.extend(["--system-prompt", system_prompt])
        cmd.append(user_message)

        def _run_subprocess() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )

        try:
            result, elapsed = self._timed_call(_run_subprocess)
        except subprocess.TimeoutExpired as err:
            raise RuntimeError(
                f"Claude CLI timed out after {self._timeout}s"
            ) from err
        except FileNotFoundError as err:
            raise RuntimeError(
                f"Claude CLI binary not found at '{cli_binary}': {err}"
            ) from err

        if result.returncode != 0:
            stderr_msg = result.stderr.strip() if result.stderr else "No error output"
            raise RuntimeError(
                f"Claude CLI exited with code {result.returncode}: {stderr_msg}"
            )

        content = result.stdout.strip()

        return AgentResponse(
            content=content,
            model_name="claude-code-cli",
            latency_seconds=round(elapsed, 3),
            raw_response=result,
            metadata={
                "adapter": "claude",
                "cli_path": cli_binary,
                "returncode": result.returncode,
            },
        )
