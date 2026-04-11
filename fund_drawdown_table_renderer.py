"""
Abstract base class for fund max-drawdown table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DrawdownTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]           # Portfolio average max-drawdown per period
    categories: list[str]          # Parallel to rows, used for grouping
    date_col_headers: list[str]
    date_rows: list[list[str]]     # Same funds as rows but cells show trough date strings


class DrawdownTableRenderer(ABC):
    @abstractmethod
    def render(self, model: DrawdownTableModel, output_path: str | None = None) -> None: ...
