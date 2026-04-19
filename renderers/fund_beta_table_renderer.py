"""
Abstract base class for fund beta table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BetaTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]            # Portfolio average beta per period
    categories: list[str]           # Parallel to rows, used for grouping
    cat_col_headers: list[str]
    cat_data_rows: list[list[str]]
    cat_total_row: list[str]
    benchmark_name: str             # Human-readable benchmark name (e.g. "FTSE 100")
    benchmark_ticker: str           # Yahoo Finance ticker (e.g. "^FTSE")


class BetaTableRenderer(ABC):
    @abstractmethod
    def render(self, model: BetaTableModel, output_path: str | None = None) -> None: ...
