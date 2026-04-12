"""
Abstract base class for fund correlation table renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CorrelationTableModel:
    col_headers: list[str]              # ["Fund Name"] + abbreviations (one per fund)
    rows: list[list[str]]               # N rows × (N+1) cols: [name, corr_0, corr_1, ...]
    categories: list[str]               # Parallel to rows, used for separator rows
    period: str                         # Period label displayed in the title (e.g. "1Y")
    n_funds: int                        # Number of funds = number of correlation columns
    abbrev_key: list[tuple[str, str]]   # [(abbrev, full_name), ...] for the key panel


class CorrelationTableRenderer(ABC):
    @abstractmethod
    def render(self, model: CorrelationTableModel, output_path: str | None = None) -> None: ...
