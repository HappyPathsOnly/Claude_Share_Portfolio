"""
Abstract base class for fund alpha table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AlphaTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]            # Portfolio average alpha per period
    categories: list[str]           # Parallel to rows, used for grouping
    cat_col_headers: list[str]
    cat_data_rows: list[list[str]]
    cat_total_row: list[str]
    benchmark_name: str             # Human-readable benchmark name (e.g. "FTSE All-World")
    benchmark_ticker: str           # Yahoo Finance ticker (e.g. "VWRL.L")
    risk_free_rate_pct: float       # Risk-free rate used in alpha calculation


class AlphaTableRenderer(ABC):
    @abstractmethod
    def render(self, model: AlphaTableModel, output_path: str | None = None) -> None: ...
