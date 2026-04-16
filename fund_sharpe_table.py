"""
Fund Portfolio – Sharpe Ratio Table
Shows the annualised Sharpe ratio for each fund over 1M, 3M, 6M, 1Y, 3Y and 5Y windows.

Sharpe = (Annualised Return – Risk-Free Rate) / Annualised Volatility

  Annualised Return  = ((P_end / P_start) ^ (252 / n_trading_days) – 1) × 100
  Annualised Vol     = std(log(P_t / P_{t-1})) × sqrt(252) × 100
  Risk-Free Rate     = UK_BASE_RATE_PCT (configurable constant below)
"""

import numpy as np
import pandas
import yfinance as yf
from collections import defaultdict

from utils.fund_utils import CSV_PATH, load_funds
from renderers.fund_sharpe_table_renderer import SharpeTableModel, SharpeTableRenderer

# ---------------------------------------------------------------------------
# Risk-free rate – approximate UK base rate (%).
# Update this when the Bank of England rate changes significantly.
# ---------------------------------------------------------------------------
UK_BASE_RATE_PCT = 4.25

PERIODS = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]

_OFFSETS = {
    "1M": pandas.DateOffset(months=1),
    "3M": pandas.DateOffset(months=3),
    "6M": pandas.DateOffset(months=6),
    "1Y": pandas.DateOffset(years=1),
    "3Y": pandas.DateOffset(years=3),
    "5Y": pandas.DateOffset(years=5),
}


def _sharpe(prices: pandas.Series, risk_free_pct: float) -> float:
    """Return the annualised Sharpe ratio for a closing-price series."""
    prices = prices.dropna()
    if len(prices) < 2:
        return float("nan")

    n = len(prices) - 1  # number of return observations
    ann_return = ((prices.iloc[-1] / prices.iloc[0]) ** (252.0 / n) - 1.0) * 100.0

    log_returns = np.log(prices / prices.shift(1)).dropna()
    ann_vol = float(log_returns.std() * np.sqrt(252) * 100.0)

    if ann_vol == 0.0:
        return float("nan")
    return (ann_return - risk_free_pct) / ann_vol


def fetch_sharpe_ratios(ticker: str) -> dict[str, float]:
    """
    Fetch 5 Y of daily closes for *ticker* and return the annualised Sharpe
    ratio for each period in PERIODS.  One API call per fund.
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
        result[label] = _sharpe(slice_prices, UK_BASE_RATE_PCT)
    return result


def _fmt(sharpe: float) -> str:
    if np.isnan(sharpe):
        return "N/A"
    return f"{sharpe:.2f}"


def build_rows(funds: list) -> tuple:
    """Return (rows, period_totals, category_totals, categories, n)."""
    rows = []
    categories = []
    period_sums: dict[str, float] = {p: 0.0 for p in PERIODS}
    category_sums: dict[str, dict[str, float]] = defaultdict(lambda: {p: 0.0 for p in PERIODS})
    category_counts: dict[str, int] = defaultdict(int)

    for f in funds:
        ratios = fetch_sharpe_ratios(f["ticker"])
        rows.append(
            [f["name"], f["ticker"]] + [_fmt(ratios[p]) for p in PERIODS]
        )
        categories.append(f["category"])
        for p in PERIODS:
            v = ratios[p]
            if not np.isnan(v):
                period_sums[p] += v
                category_sums[f["category"]][p] += v
        category_counts[f["category"]] += 1

    n = len(funds)
    return rows, period_sums, category_sums, category_counts, categories, n


def build_table_model(funds: list) -> SharpeTableModel:
    rows, period_sums, category_sums, category_counts, categories, n = build_rows(funds)

    col_headers = ["Fund Name", "Ticker"] + [f"{p} Sharpe" for p in PERIODS]

    avg_row = ["", "Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    cat_col_headers = ["Category"] + [f"{p} Sharpe" for p in PERIODS]

    cat_data_rows = []
    for cat in sorted(category_sums):
        count = category_counts[cat]
        cat_data_rows.append(
            [cat] + [_fmt(category_sums[cat][p] / count) for p in PERIODS]
        )

    cat_total_row = ["Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    return SharpeTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=avg_row,
        categories=categories,
        cat_col_headers=cat_col_headers,
        cat_data_rows=cat_data_rows,
        cat_total_row=cat_total_row,
        risk_free_rate_pct=UK_BASE_RATE_PCT,
    )


def main(renderer: SharpeTableRenderer):
    print("Fetching fund data for Sharpe ratio table...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund Sharpe ratio table")
    args = parser.parse_args()

    from GUI.Bokeh.fund_sharpe_table_bokeh import BokehSharpeTableRenderer
    main(BokehSharpeTableRenderer())
