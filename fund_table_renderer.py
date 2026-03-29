"""
Abstract base class for fund table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TableModel:
    col_headers: list[str]
    rows: list[list[str]]
    total_row: list[str]
    categories: list[str]  # parallel to rows, used for grouping/colouring


class TableRenderer(ABC):
    @abstractmethod
    def render(self, model: TableModel) -> None: ...
