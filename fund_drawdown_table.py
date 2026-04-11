"""
Fund Portfolio - Max Drawdown Table
Shows the worst peak-to-trough drop for each fund over 1M, 3M, 6M, 1Y, 3Y and 5Y windows.

Max drawdown = max((peak - trough) / peak) where the trough follows the peak.
Values are expressed as negative percentages (e.g. -15.30 %).
"""

import pandas
import yfinance as yf

from fund_utils import CSV_PATH, load_funds, _max_drawdown_calculation, _OFFSETS
from fund_drawdown_table_renderer import DrawdownTableModel, DrawdownTableRenderer

PERIODS = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]

def fetch_drawdowns(ticker: str) -> dict[str, tuple[float, str]]:
    """
    Fetch 5Y of daily closes for *ticker* and return (max_drawdown_pct, trough_date)
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
        result[label] = _max_drawdown_calculation(slice_prices)
    return result


def _fmt(drawdown: float) -> str:
    return f"{drawdown:.2f}%"


def build_rows(funds: list) -> tuple:
    """Return (rows, period_sums, date_rows, categories, n)."""
    rows = []
    date_rows = []
    categories = []
    period_sums: dict[str, float] = {p: 0.0 for p in PERIODS}

    for f in funds:
        drawdowns = fetch_drawdowns(f["ticker"])
        rows.append(
            [f["name"], f["ticker"]] + [_fmt(drawdowns[p][0]) for p in PERIODS]
        )
        date_rows.append(
            [f["name"], f["ticker"]] + [drawdowns[p][1] for p in PERIODS]
        )
        categories.append(f["category"])
        for p in PERIODS:
            period_sums[p] += drawdowns[p][0]

    n = len(funds)
    return rows, period_sums, date_rows, categories, n


def build_table_model(funds: list) -> DrawdownTableModel:
    rows, period_sums, date_rows, categories, n = build_rows(funds)

    col_headers = ["Fund Name", "Ticker"] + [f"{p} MDD" for p in PERIODS]
    avg_row = ["", "Portfolio Avg"] + [_fmt(period_sums[p] / n) for p in PERIODS]

    date_col_headers = ["Fund Name", "Ticker"] + [f"{p} Trough Date" for p in PERIODS]

    return DrawdownTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=avg_row,
        categories=categories,
        date_col_headers=date_col_headers,
        date_rows=date_rows,
    )


def main(renderer: DrawdownTableRenderer):
    print("Fetching fund data for max-drawdown table...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund max-drawdown table")
    parser.add_argument("--bokeh", action="store_true", help="Use Bokeh renderer (opens in browser)")
    args = parser.parse_args()

    if args.bokeh:
        from GUI.Bokeh.fund_drawdown_table_bokeh import BokehDrawdownTableRenderer
        main(BokehDrawdownTableRenderer())
    else:
        raise NotImplementedError("Only the Bokeh renderer is implemented for the drawdown table.")
