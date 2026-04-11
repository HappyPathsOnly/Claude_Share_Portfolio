"""
Abstract base class for fund volatility table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VolatilityTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]           # Portfolio average volatility per period
    categories: list[str]          # Parallel to rows, used for grouping
    cat_col_headers: list[str]
    cat_data_rows: list[list[str]]
    cat_total_row: list[str]


class VolatilityTableRenderer(ABC):
    @abstractmethod
    def render(self, model: VolatilityTableModel, output_path: str | None = None) -> None: ...
