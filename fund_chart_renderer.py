"""
Abstract base class for fund chart renderers.
Implement this to provide alternative display backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ChartModel:
    df: Any                        # pd.DataFrame of initial period data
    period_label: str              # human-readable label for the initial period (e.g. "1Y")
    fund_name: str
    period_labels: list[str]       # ordered list of all period button labels
    fetch_fn: Callable[[str], Any] # fetch_fn(label: str) -> pd.DataFrame


class ChartRenderer(ABC):
    @abstractmethod
    def render(self, model: ChartModel) -> None: ...
