"""
Fund Portfolio – Beta Table
Shows the beta of each fund relative to a benchmark over 1M, 3M, 6M, 1Y, 3Y and 5Y windows.

Beta = Covariance(fund returns, benchmark returns) / Variance(benchmark returns)

Daily log returns are used for both the fund and the benchmark.
The benchmark is fetched once and reused across all funds.
"""

import numpy as np
import pandas
import yfinance as yf
from collections import defaultdict

from utils.fund_utils import CSV_PATH, load_funds
from renderers.fund_beta_table_renderer import BetaTableModel, BetaTableRenderer

# ---------------------------------------------------------------------------
# Benchmark – FTSE 100 (^FTSE) is the natural UK equity benchmark.
# Change BENCHMARK_TICKER / BENCHMARK_NAME if a different index is preferred.
# ---------------------------------------------------------------------------
BENCHMARK_TICKER = "VWRL.L"
BENCHMARK_NAME   = "FTSE All-World"

PERIODS = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]

_OFFSETS = {
    "1M": pandas.DateOffset(months=1),
    "3M": pandas.DateOffset(months=3),
    "6M": pandas.DateOffset(months=6),
    "1Y": pandas.DateOffset(years=1),
    "3Y": pandas.DateOffset(years=3),
    "5Y": pandas.DateOffset(years=5),
}


def _beta(fund_prices: pandas.Series, bench_prices: pandas.Series) -> float:
    """
    Return the beta of *fund_prices* relative to *bench_prices*.

    Both series are aligned on their shared trading dates before computing
    daily log returns.  Returns NaN when fewer than two shared dates exist
    or when benchmark variance is zero.
    """
    # Align on shared dates
    combined = pandas.DataFrame({"fund": fund_prices, "bench": bench_prices}).dropna()
    if len(combined) < 2:
        return float("nan")

    fund_ret  = np.log(combined["fund"]  / combined["fund"].shift(1)).dropna()
    bench_ret = np.log(combined["bench"] / combined["bench"].shift(1)).dropna()

    # Re-align after differencing (first row becomes NaN)
    fund_ret, bench_ret = fund_ret.align(bench_ret, join="inner")

    bench_var = float(bench_ret.var())
    if bench_var == 0.0:
        return float("nan")

    cov = float(fund_ret.cov(bench_ret))
    return cov / bench_var


def fetch_benchmark(period: str = "5y") -> pandas.Series:
    """Fetch 5 Y of daily closes for the benchmark.  Called once."""
    bench = yf.Ticker(BENCHMARK_TICKER)
    df = bench.history(period=period)
    if df.empty:
        raise ValueError(f"No data returned for benchmark {BENCHMARK_TICKER!r}")
    return df["Close"]


def fetch_betas(ticker: str, bench_closes: pandas.Series) -> dict[str, float]:
    """
    Fetch 5 Y of daily closes for *ticker* and return the beta relative to
    *bench_closes* for each period in PERIODS.  One API call per fund.
    """
    fund = yf.Ticker(ticker)
    df = fund.history(period="5y")
    if df.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")

    fund_closes = df["Close"]
    latest = min(fund_closes.index[-1], bench_closes.index[-1])

    result = {}
    for label, offset in _OFFSETS.items():
        start = latest - offset
        fund_slice  = fund_closes.loc[fund_closes.index   >= start]
        bench_slice = bench_closes.loc[bench_closes.index >= start]
        result[label] = _beta(fund_slice, bench_slice)
    return result


def _fmt(beta: float) -> str:
    if np.isnan(beta):
        return "N/A"
    return f"{beta:.2f}"


def build_rows(funds: list, bench_closes: pandas.Series) -> tuple:
    """Return (rows, period_sums, category_sums, category_counts, categories, n)."""
    rows = []
    categories = []
    period_sums: dict[str, float] = {p: 0.0 for p in PERIODS}
    category_sums: dict[str, dict[str, float]] = defaultdict(lambda: {p: 0.0 for p in PERIODS})
    category_counts: dict[str, int] = defaultdict(int)

    for f in funds:
        betas = fetch_betas(f["ticker"], bench_closes)
        rows.append(
            [f["name"], f["ticker"]] + [_fmt(betas[p]) for p in PERIODS]
        )
        categories.append(f["category"])
        for p in PERIODS:
            v = betas[p]
            if not np.isnan(v):
                period_sums[p] += v
                category_sums[f["category"]][p] += v
        category_counts[f["category"]] += 1

    n = len(funds)
    return rows, period_sums, category_sums, category_counts, categories, n


def build_table_model(funds: list) -> BetaTableModel:
    print(f"Fetching benchmark data ({BENCHMARK_TICKER})...")
    bench_closes = fetch_benchmark()

    rows, period_sums, category_sums, category_counts, categories, n = build_rows(funds, bench_closes)

    col_headers = ["Fund Name", "Ticker"] + [f"{p} Beta" for p in PERIODS]

    avg_row = ["", "Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    cat_col_headers = ["Category"] + [f"{p} Beta" for p in PERIODS]

    cat_data_rows = []
    for cat in sorted(category_sums):
        count = category_counts[cat]
        cat_data_rows.append(
            [cat] + [_fmt(category_sums[cat][p] / count) for p in PERIODS]
        )

    cat_total_row = ["Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    return BetaTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=avg_row,
        categories=categories,
        cat_col_headers=cat_col_headers,
        cat_data_rows=cat_data_rows,
        cat_total_row=cat_total_row,
        benchmark_name=BENCHMARK_NAME,
        benchmark_ticker=BENCHMARK_TICKER,
    )


def main(renderer: BetaTableRenderer):
    print("Fetching fund data for beta table...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund beta table")
    args = parser.parse_args()

    from GUI.Bokeh.fund_beta_table_bokeh import BokehBetaTableRenderer
    main(BokehBetaTableRenderer())
