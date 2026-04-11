"""
Abstract base class for fund value table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ValueTableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]
    categories: list[str]        # parallel to rows, used for grouping
    cat_col_headers: list[str]
    cat_data_rows: list[list[str]]
    cat_total_row: list[str]


class ValueTableRenderer(ABC):
    @abstractmethod
    def render(self, model: ValueTableModel) -> None: ...
