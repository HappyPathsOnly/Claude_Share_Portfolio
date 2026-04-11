"""
Fund Portfolio - Historical Volatility Table
Shows annualised historical volatility for each fund over 1M, 3M, 6M, 1Y, 3Y and 5Y windows.

Volatility = annualised std dev of daily log returns = std(log(P_t/P_{t-1})) * sqrt(252).
"""

import numpy as np
import pandas
import yfinance as yf
from collections import defaultdict

from utils.fund_utils import CSV_PATH, load_funds
from fund_volatility_table_renderer import VolatilityTableModel, VolatilityTableRenderer

PERIODS = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]

_OFFSETS = {
    "1M": pandas.DateOffset(months=1),
    "3M": pandas.DateOffset(months=3),
    "6M": pandas.DateOffset(months=6),
    "1Y": pandas.DateOffset(years=1),
    "3Y": pandas.DateOffset(years=3),
    "5Y": pandas.DateOffset(years=5),
}


def _annualised_vol(prices: pandas.Series) -> float:
    """Annualised volatility (%) from a closing-price series."""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    return float(log_returns.std() * np.sqrt(252) * 100)


def fetch_volatilities(ticker: str) -> dict[str, float]:
    """
    Fetch 5Y of daily closes for *ticker* and return annualised volatility
    for each period in PERIODS.  One API call per fund.
    """
    fund = yf.Ticker(ticker)
    df = fund.history(period="5y")
    if df.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")

    latest = df.index[-1]
    result = {}
    for label, offset in _OFFSETS.items():
        start = latest - offset
        slice_prices = df.loc[df.index >= start, "Close"]
        result[label] = _annualised_vol(slice_prices)
    return result


def _fmt(vol: float) -> str:
    return f"{vol:.2f}%"


def build_rows(funds: list) -> tuple:
    """Return (rows, period_totals, category_totals, categories)."""
    rows = []
    categories = []
    period_sums: dict[str, float] = {p: 0.0 for p in PERIODS}
    category_sums: dict[str, dict[str, float]] = defaultdict(lambda: {p: 0.0 for p in PERIODS})
    category_counts: dict[str, int] = defaultdict(int)

    for f in funds:
        vols = fetch_volatilities(f["ticker"])
        rows.append(
            [f["name"], f["ticker"]] + [_fmt(vols[p]) for p in PERIODS]
        )
        categories.append(f["category"])
        for p in PERIODS:
            period_sums[p] += vols[p]
            category_sums[f["category"]][p] += vols[p]
        category_counts[f["category"]] += 1

    n = len(funds)
    return rows, period_sums, category_sums, category_counts, categories, n


def build_table_model(funds: list) -> VolatilityTableModel:
    rows, period_sums, category_sums, category_counts, categories, n = build_rows(funds)

    col_headers = ["Fund Name", "Ticker"] + [f"{p} Vol" for p in PERIODS]

    avg_row = ["", "Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    cat_col_headers = ["Category"] + [f"{p} Vol" for p in PERIODS]

    cat_data_rows = []
    for cat in sorted(category_sums):
        count = category_counts[cat]
        cat_data_rows.append(
            [cat] + [_fmt(category_sums[cat][p] / count) for p in PERIODS]
        )

    cat_total_row = ["Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    return VolatilityTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=avg_row,
        categories=categories,
        cat_col_headers=cat_col_headers,
        cat_data_rows=cat_data_rows,
        cat_total_row=cat_total_row,
    )


def main(renderer: VolatilityTableRenderer):
    print("Fetching fund data for volatility table...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund historical volatility table")
    args = parser.parse_args()

    from GUI.Bokeh.fund_volatility_table_bokeh import BokehVolatilityTableRenderer
    main(BokehVolatilityTableRenderer())
