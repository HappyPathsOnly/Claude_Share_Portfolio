"""
Abstract base class for fund Sharpe ratio table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SharpeTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]            # Portfolio average Sharpe per period
    categories: list[str]           # Parallel to rows, used for grouping
    cat_col_headers: list[str]
    cat_data_rows: list[list[str]]
    cat_total_row: list[str]
    risk_free_rate_pct: float       # Risk-free rate used (for display)


class SharpeTableRenderer(ABC):
    @abstractmethod
    def render(self, model: SharpeTableModel, output_path: str | None = None) -> None: ...
