"""Utilities for timing shell command execution."""

import subprocess
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TimingResult:
    command: str
    input_size: int
    elapsed_seconds: float
    returncode: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.returncode == 0


def time_command(
    command: str,
    input_size: int,
    capture_output: bool = False,
    timeout: Optional[float] = None,
) -> TimingResult:
    """Run a shell command and measure its wall-clock execution time."""
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return TimingResult(
            command=command,
            input_size=input_size,
            elapsed_seconds=elapsed,
            returncode=-1,
            stderr="TimeoutExpired",
        )
    elapsed = time.perf_counter() - start
    return TimingResult(
        command=command,
        input_size=input_size,
        elapsed_seconds=elapsed,
        returncode=result.returncode,
        stdout=result.stdout if capture_output else None,
        stderr=result.stderr if capture_output else None,
    )
