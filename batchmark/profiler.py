"""Memory and CPU profiling utilities for timed command runs."""

from __future__ import annotations

import resource
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult, time_command


@dataclass
class ProfiledResult:
    timing: TimingResult
    max_rss_kb: int  # peak resident set size in kilobytes
    user_time_s: float
    sys_time_s: float

    @property
    def success(self) -> bool:
        return self.timing.returncode == 0


def _rusage_after(proc: subprocess.Popen) -> resource.struct_rusage:
    """Wait for process and return resource usage."""
    _, _, rusage = resource.wait4(proc.pid, 0)
    return rusage


def profile_command(
    cmd: str,
    timeout: Optional[float] = None,
    capture_output: bool = False,
) -> ProfiledResult:
    """Run *cmd* and collect timing + basic resource usage.

    Falls back to zeros for rusage fields on platforms where
    ``resource.wait4`` is unavailable (e.g. Windows).
    """
    import time

    start = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            timeout=timeout,
            capture_output=capture_output,
        )
        elapsed = time.perf_counter() - start
        returncode = completed.returncode
        stdout = completed.stdout or b""
        stderr = completed.stderr or b""
    except subprocess.TimeoutExpired:
        elapsed = timeout or 0.0
        returncode = -1
        stdout = b""
        stderr = b""

    timing = TimingResult(
        command=cmd,
        size=0,
        duration=elapsed,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )

    try:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        max_rss_kb = usage.ru_maxrss
        user_time_s = usage.ru_utime
        sys_time_s = usage.ru_stime
    except Exception:
        max_rss_kb = 0
        user_time_s = 0.0
        sys_time_s = 0.0

    return ProfiledResult(
        timing=timing,
        max_rss_kb=max_rss_kb,
        user_time_s=user_time_s,
        sys_time_s=sys_time_s,
    )
