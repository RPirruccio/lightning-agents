"""
Agent Logger - Streaming visibility into agent execution.

Logs tool calls, results, and execution stats to both stdout and log files.
"""

from datetime import datetime
from pathlib import Path
from typing import TextIO


class AgentLogger:
    """Streaming logger for agent execution visibility."""

    def __init__(self, agent_id: str, log_dir: Path | None = None):
        """Initialize logger for an agent run.

        Args:
            agent_id: ID of the agent being run
            log_dir: Directory for log files (default: project_root/logs)
        """
        self.agent_id = agent_id
        self.start_time = datetime.now()
        self.tool_calls = 0

        # Set up log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create log file: logs/{agent_id}.log (overwrites on each run)
        self.log_file = log_dir / f"{agent_id}.log"
        self._file: TextIO | None = None

    def __enter__(self):
        """Context manager entry - open log file."""
        self._file = open(self.log_file, "w")
        self._write_header()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager exit - close log file."""
        if self._file:
            self._file.close()
            self._file = None

    def _write_header(self):
        """Write log header."""
        header = f"""
{'=' * 60}
Agent: {self.agent_id}
Started: {self.start_time.isoformat()}
{'=' * 60}
"""
        self._log(header)

    def _log(self, msg: str, end: str = "\n", flush: bool = True):
        """Log to both stdout and file."""
        print(msg, end=end, flush=flush)
        if self._file:
            self._file.write(msg + end)
            if flush:
                self._file.flush()

    def text(self, text: str):
        """Log streamed text from assistant."""
        self._log(text, end="", flush=True)

    def tool_use(self, tool_name: str, tool_input: dict | None = None):
        """Log a tool invocation."""
        self.tool_calls += 1

        # Format input summary
        input_summary = ""
        if tool_input:
            input_str = str(tool_input)
            if len(input_str) > 150:
                input_summary = f"\n      Input: {input_str[:150]}..."
            else:
                input_summary = f"\n      Input: {input_str}"

        self._log(f"\n  \u25b8 [{tool_name}]{input_summary}")

    def tool_result(self, content: str | None = None, is_error: bool = False):
        """Log a tool result."""
        if content:
            # Truncate long results
            summary = content[:300] + "..." if len(content) > 300 else content
            prefix = "\u2717 Error" if is_error else "\u2192 Result"
            self._log(f"    {prefix}: {summary}")

    def execution_complete(self, input_tokens: int = 0, output_tokens: int = 0, cost: float = 0.0):
        """Log execution completion with stats."""
        elapsed = datetime.now() - self.start_time

        self._log(f"\n\n{'=' * 60}")
        self._log(f"Execution complete!")
        self._log(f"Duration: {elapsed.total_seconds():.2f}s")
        self._log(f"Tool calls: {self.tool_calls}")
        if input_tokens or output_tokens:
            self._log(f"Tokens: {input_tokens} in / {output_tokens} out")
        if cost:
            self._log(f"Cost: ${cost:.4f}")
        self._log(f"Log file: {self.log_file}")
        self._log(f"{'=' * 60}\n")

    def error(self, error_msg: str):
        """Log an error."""
        self._log(f"\n\u274c ERROR: {error_msg}")
