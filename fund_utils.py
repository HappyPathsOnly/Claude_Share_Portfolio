"""
Shared utilities for fund data loading and price fetching.
"""

import csv
import os
import pandas
import yfinance as yf

_dir = os.path.dirname(__file__)
CSV_PATH = os.path.join(_dir, "funds.csv")
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(_dir, "funds.example.csv")


def load_funds(csv_path: str) -> list:
    """Load fund definitions from a CSV file (columns: name, ticker, units)."""
    funds = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            funds.append({
                "name": row["name"].strip(),
                "ticker": row["ticker"].strip(),
                "units": int(row["units"].strip()),
            })
    return funds


def fetch_prices_gbp(ticker: str) -> tuple[float, float, float, float, float]:
    """Fetch latest, 1W, 1M, 6M and 1Y closing prices in GBP."""
    fund = yf.Ticker(ticker)
    df = fund.history(period="13mo")
    if df.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")

    def price_at(days=None, months=None):
        if days:
            target = df.index[-1] - pandas.DateOffset(days=days)
        else:
            target = df.index[-1] - pandas.DateOffset(months=months)
        idx = df.index.get_indexer([target], method="nearest")[0]
        return df["Close"].iloc[idx]

    return df["Close"].iloc[-1], price_at(days=7), price_at(months=1), price_at(months=6), price_at(months=12)
