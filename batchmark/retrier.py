"""Retry logic for flaky commands."""

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult, time_command


@dataclass
class RetryConfig:
    max_attempts: int = 3
    retry_on_failure: bool = True
    retry_on_timeout: bool = False


@dataclass
class RetriedResult:
    result: TimingResult
    attempts: int
    all_results: List[TimingResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _should_retry(result: TimingResult, config: RetryConfig) -> bool:
    if result.returncode == -1 and config.retry_on_timeout:
        return True
    if result.returncode != 0 and result.returncode != -1 and config.retry_on_failure:
        return True
    return False


def run_with_retry(
    cmd: List[str],
    config: Optional[RetryConfig] = None,
    timeout: Optional[float] = None,
) -> RetriedResult:
    """Run a command, retrying up to config.max_attempts times."""
    if config is None:
        config = RetryConfig()

    all_results: List[TimingResult] = []

    for attempt in range(1, config.max_attempts + 1):
        result = time_command(cmd, timeout=timeout)
        all_results.append(result)

        if result.returncode == 0:
            return RetriedResult(result=result, attempts=attempt, all_results=all_results)

        if attempt < config.max_attempts and _should_retry(result, config):
            continue

        break

    return RetriedResult(result=all_results[-1], attempts=len(all_results), all_results=all_results)
