"""
Shared utilities for fund data loading and price fetching.
"""

import csv
import os
import pandas
import yfinance as yf

PERIODS = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]

_OFFSETS = {
    "1M": pandas.DateOffset(months=1),
    "3M": pandas.DateOffset(months=3),
    "6M": pandas.DateOffset(months=6),
    "1Y": pandas.DateOffset(years=1),
    "3Y": pandas.DateOffset(years=3),
    "5Y": pandas.DateOffset(years=5),
}

_root = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(_root, "funds.csv")
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(_root, "funds.example.csv")


def load_funds(csv_path: str) -> list:
    """Load fund definitions from a CSV file (columns: name, ticker, units, category)."""
    funds = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("name", "").strip():
                continue
            funds.append({
                "name": row["name"].strip(),
                "ticker": row["ticker"].strip(),
                "units": float(row["units"].strip()),
                "category": row.get("category", "").strip(),
            })
    return funds


def fetch_prices_gbp(ticker: str) -> tuple[float, float, float, float, float, float]:
    """Fetch latest, previous day, 1W, 1M, 6M and 1Y closing prices in GBP."""
    fund = yf.Ticker(ticker)
    df = fund.history(period="13mo")
    if df.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")
    divisor = 100.0 if fund.fast_info.get("currency") == "GBp" else 1.0

    def price_at(days=None, months=None):
        if days:
            target = df.index[-1] - pandas.DateOffset(days=days)
        else:
            target = df.index[-1] - pandas.DateOffset(months=months)
        idx = df.index.get_indexer([target], method="nearest")[0]
        return df["Close"].iloc[idx]

    return (
        df["Close"].iloc[-1] / divisor,   # latest
        df["Close"].iloc[-2] / divisor,   # previous trading day
        price_at(days=7) / divisor,
        price_at(months=1) / divisor,
        price_at(months=6) / divisor,
        price_at(months=12) / divisor,
    )



def _max_drawdown_calculation(prices: pandas.Series) -> tuple[float, str]:
    """Calculate the maximum drawdown over a price series.

    The maximum drawdown is the largest peak-to-trough decline expressed as a
    percentage of the peak price. It is computed by tracking the running maximum
    price and measuring how far each subsequent price has fallen from that peak.

    Args:
        prices: A pandas Series of closing prices indexed by date.

    Returns:
        A tuple of (drawdown_pct, date_str) where drawdown_pct is the maximum
        drawdown as a negative percentage (e.g. -15.3) and date_str is the date
        of the trough formatted as "DD Mon YYYY". Returns (0.0, "N/A") if the
        series has fewer than two non-NaN values.
    """
    prices = prices.dropna()
    if len(prices) < 2:
        return 0.0, "N/A"
    rolling_max = prices.cummax()
    drawdowns = (prices - rolling_max) / rolling_max * 100
    min_idx = drawdowns.idxmin()
    return float(drawdowns.min()), min_idx.strftime("%d %b %Y")
