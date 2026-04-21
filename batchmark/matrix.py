"""Matrix runner: execute commands across multiple (size, variant) combinations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult, time_command


@dataclass
class MatrixCell:
    size: int
    variant: str
    result: TimingResult


@dataclass
class MatrixConfig:
    command_template: str
    sizes: List[int]
    variants: Dict[str, str]  # variant_name -> extra_args or substitution
    runs: int = 1
    timeout: Optional[float] = None
    size_placeholder: str = "{size}"
    variant_placeholder: str = "{variant}"


def _build_matrix_command(template: str, size: int, variant: str,
                          size_ph: str, variant_ph: str) -> str:
    """Substitute size and variant placeholders in the command template."""
    if size_ph not in template and variant_ph not in template:
        raise ValueError(
            f"Template must contain '{size_ph}' or '{variant_ph}': {template!r}"
        )
    cmd = template.replace(size_ph, str(size))
    cmd = cmd.replace(variant_ph, variant)
    return cmd


def run_matrix(config: MatrixConfig) -> List[MatrixCell]:
    """Run all (size, variant) combinations and return MatrixCell results."""
    cells: List[MatrixCell] = []
    for size in config.sizes:
        for variant_name, variant_value in config.variants.items():
            cmd = _build_matrix_command(
                config.command_template,
                size,
                variant_value,
                config.size_placeholder,
                config.variant_placeholder,
            )
            for _ in range(config.runs):
                result = time_command(cmd, timeout=config.timeout)
                cells.append(MatrixCell(size=size, variant=variant_name, result=result))
    return cells
