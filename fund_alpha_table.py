"""
Fund Portfolio – Alpha Table
Shows Jensen's Alpha for each fund relative to a benchmark over 1M, 3M, 6M, 1Y, 3Y and 5Y windows.

Alpha = Fund Annualised Return – [Risk-Free Rate + Beta × (Benchmark Annualised Return – Risk-Free Rate)]

  Annualised Return = ((P_end / P_start) ^ (252 / n_trading_days) – 1) × 100  (%)
  Beta              = Covariance(fund log returns, benchmark log returns) / Variance(benchmark log returns)
  Risk-Free Rate    = UK_BASE_RATE_PCT (configurable constant below)

Alpha > 0 → the fund outperformed what its market exposure alone would predict
Alpha < 0 → the fund underperformed relative to its market exposure
"""

import numpy as np
import pandas
import yfinance as yf
from collections import defaultdict

from utils.fund_utils import CSV_PATH, load_funds
from renderers.fund_alpha_table_renderer import AlphaTableModel, AlphaTableRenderer

# ---------------------------------------------------------------------------
# Benchmark – FTSE All World is the all world equity benchmark.
# ---------------------------------------------------------------------------
BENCHMARK_TICKER = "VWRL.L"
BENCHMARK_NAME   = "FTSE All-World"

# ---------------------------------------------------------------------------
# Risk-free rate – approximate UK base rate (%).
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


def _alpha(
    fund_prices: pandas.Series,
    bench_prices: pandas.Series,
    risk_free_pct: float,
) -> float:
    """
    Return Jensen's Alpha (%) for *fund_prices* relative to *bench_prices*.

    Both series are aligned on shared trading dates.  Returns NaN when fewer
    than two shared dates exist or when benchmark variance is zero.
    """
    combined = pandas.DataFrame({"fund": fund_prices, "bench": bench_prices}).dropna()
    if len(combined) < 2:
        return float("nan")

    n = len(combined) - 1
    fund_ann_ret  = ((combined["fund"].iloc[-1]  / combined["fund"].iloc[0])  ** (252.0 / n) - 1.0) * 100.0
    bench_ann_ret = ((combined["bench"].iloc[-1] / combined["bench"].iloc[0]) ** (252.0 / n) - 1.0) * 100.0

    fund_log  = np.log(combined["fund"]  / combined["fund"].shift(1)).dropna()
    bench_log = np.log(combined["bench"] / combined["bench"].shift(1)).dropna()
    fund_log, bench_log = fund_log.align(bench_log, join="inner")

    bench_var = float(bench_log.var())
    if bench_var == 0.0:
        return float("nan")

    beta = float(fund_log.cov(bench_log)) / bench_var
    return fund_ann_ret - (risk_free_pct + beta * (bench_ann_ret - risk_free_pct))


def fetch_benchmark(period: str = "5y") -> pandas.Series:
    """Fetch 5 Y of daily closes for the benchmark.  Called once."""
    bench = yf.Ticker(BENCHMARK_TICKER)
    df = bench.history(period=period)
    if df.empty:
        raise ValueError(f"No data returned for benchmark {BENCHMARK_TICKER!r}")
    return df["Close"]


def fetch_alphas(ticker: str, bench_closes: pandas.Series) -> dict[str, float]:
    """
    Fetch 5 Y of daily closes for *ticker* and return Jensen's Alpha relative
    to *bench_closes* for each period in PERIODS.  One API call per fund.
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
        result[label] = _alpha(fund_slice, bench_slice, UK_BASE_RATE_PCT)
    return result


def _fmt(alpha: float) -> str:
    if np.isnan(alpha):
        return "N/A"
    return f"{alpha:.2f}%"


def build_rows(funds: list, bench_closes: pandas.Series) -> tuple:
    """Return (rows, period_sums, category_sums, category_counts, categories, n)."""
    rows = []
    categories = []
    period_sums: dict[str, float] = {p: 0.0 for p in PERIODS}
    category_sums: dict[str, dict[str, float]] = defaultdict(lambda: {p: 0.0 for p in PERIODS})
    category_counts: dict[str, int] = defaultdict(int)

    for f in funds:
        alphas = fetch_alphas(f["ticker"], bench_closes)
        rows.append(
            [f["name"], f["ticker"]] + [_fmt(alphas[p]) for p in PERIODS]
        )
        categories.append(f["category"])
        for p in PERIODS:
            v = alphas[p]
            if not np.isnan(v):
                period_sums[p] += v
                category_sums[f["category"]][p] += v
        category_counts[f["category"]] += 1

    n = len(funds)
    return rows, period_sums, category_sums, category_counts, categories, n


def build_table_model(funds: list) -> AlphaTableModel:
    print(f"Fetching benchmark data ({BENCHMARK_TICKER})...")
    bench_closes = fetch_benchmark()

    rows, period_sums, category_sums, category_counts, categories, n = build_rows(funds, bench_closes)

    col_headers = ["Fund Name", "Ticker"] + [f"{p} Alpha" for p in PERIODS]

    avg_row = ["", "Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    cat_col_headers = ["Category"] + [f"{p} Alpha" for p in PERIODS]

    cat_data_rows = []
    for cat in sorted(category_sums):
        count = category_counts[cat]
        cat_data_rows.append(
            [cat] + [_fmt(category_sums[cat][p] / count) for p in PERIODS]
        )

    cat_total_row = ["Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    return AlphaTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=avg_row,
        categories=categories,
        cat_col_headers=cat_col_headers,
        cat_data_rows=cat_data_rows,
        cat_total_row=cat_total_row,
        benchmark_name=BENCHMARK_NAME,
        benchmark_ticker=BENCHMARK_TICKER,
        risk_free_rate_pct=UK_BASE_RATE_PCT,
    )


def main(renderer: AlphaTableRenderer):
    print("Fetching fund data for alpha table...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund alpha table")
    args = parser.parse_args()

    from GUI.Bokeh.fund_alpha_table_bokeh import BokehAlphaTableRenderer
    main(BokehAlphaTableRenderer())
