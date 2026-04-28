"""cutter.py – slice a result list into fixed-size chunks.

Useful when you want to process or display results in batches of N
without the full pagination machinery of pager.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass(frozen=True)
class CutConfig:
    chunk_size: int = 10
    drop_remainder: bool = False

    def __post_init__(self) -> None:
        if self.chunk_size < 1:
            raise ValueError("chunk_size must be >= 1")


@dataclass(frozen=True)
class Chunk:
    index: int          # 0-based chunk index
    results: List[TimingResult]

    @property
    def size(self) -> int:
        return len(self.results)

    @property
    def successful(self) -> int:
        return sum(1 for r in self.results if r.returncode == 0)

    @property
    def failed(self) -> int:
        return self.size - self.successful


def cut_results(
    results: List[TimingResult],
    config: Optional[CutConfig] = None,
) -> List[Chunk]:
    """Split *results* into chunks according to *config*."""
    if config is None:
        config = CutConfig()

    chunks: List[Chunk] = []
    n = config.chunk_size
    total = len(results)
    num_full_chunks = total // n
    remainder = total % n

    for i in range(num_full_chunks):
        chunks.append(Chunk(index=i, results=results[i * n : (i + 1) * n]))

    if remainder and not config.drop_remainder:
        chunks.append(
            Chunk(index=num_full_chunks, results=results[num_full_chunks * n :])
        )

    return chunks


def format_cut_summary(chunks: List[Chunk]) -> str:
    """Return a one-line summary of the cut operation."""
    total_results = sum(c.size for c in chunks)
    total_ok = sum(c.successful for c in chunks)
    return (
        f"cut: {len(chunks)} chunk(s), "
        f"{total_results} result(s), "
        f"{total_ok} successful"
    )
