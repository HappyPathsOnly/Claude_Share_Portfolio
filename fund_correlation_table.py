"""
Fund Portfolio - Inter-Fund Correlation Matrix
Shows pairwise Pearson correlation of daily returns between all funds over a 1-year window.

A value close to +1 means two funds move almost in lockstep (poor diversification).
A value close to 0 means they move independently (good diversification).
A negative value means they tend to move in opposite directions (excellent diversification).
"""

import re
from collections import Counter

import pandas
import yfinance as yf

from utils.fund_utils import CSV_PATH, load_funds
from renderers.fund_correlation_table_renderer import CorrelationTableModel, CorrelationTableRenderer

PERIOD = "1Y"

# Words that carry no identifying information in a fund name and should be
# skipped when building the abbreviation.
_ABBREV_SKIP = {
    "fund", "acc", "accumulation", "w", "a", "b", "c", "i", "inst",
    "plc", "etf", "ucits", "class", "gbp", "ex", "and", "the", "of",
    "index",
}


def _abbrev_single(name: str) -> str:
    """Return a short uppercase initialism for one fund name."""
    tokens = re.split(r"[\s&\-/]+", name)
    parts = []
    for tok in tokens:
        clean = tok.rstrip(".,")
        if not clean or clean.lower() in _ABBREV_SKIP:
            continue
        # Leading digits (e.g. "80%" → "80", "2035" → "2035")
        m = re.match(r"(\d+)", clean)
        if m:
            parts.append(m.group(1))
        elif clean[0].isalpha():
            parts.append(clean[0].upper())
    return "".join(parts) or name[:4].upper()


def _make_abbreviations(names: list[str]) -> list[str]:
    """Return a list of unique abbreviations, one per fund name."""
    raw = [_abbrev_single(n) for n in names]
    counts = Counter(raw)
    occurrence: dict[str, int] = {}
    result = []
    for ab in raw:
        if counts[ab] == 1:
            result.append(ab)
        else:
            occurrence[ab] = occurrence.get(ab, 0) + 1
            result.append(f"{ab}{occurrence[ab]}")
    return result


def fetch_correlation_matrix(funds: list) -> tuple[list[str], list[str], pandas.DataFrame]:
    """
    Fetch 1 year of daily closes for every fund and return:
      - names:   list of display names (one per fund)
      - tickers: list of ticker symbols (one per fund)
      - corr:    N×N Pearson correlation DataFrame of daily returns
    """
    closes = {}
    for f in funds:
        ticker = f["ticker"]
        fund_ticker = yf.Ticker(ticker)
        df = fund_ticker.history(period="1y")
        if df.empty:
            raise ValueError(f"No data returned for ticker {ticker!r}")
        series = df["Close"]
        if series.index.tz:
            series = series.tz_convert(None)
        series.index = series.index.normalize()
        closes[f["name"]] = series

    price_df = pandas.DataFrame(closes).dropna()
    returns = price_df.pct_change().dropna()
    corr = returns.corr()

    names = [f["name"] for f in funds]
    tickers = [f["ticker"] for f in funds]
    return names, tickers, corr



def _fmt(val: float) -> str:
    return f"{val:.2f}"


def build_table_model(funds: list) -> CorrelationTableModel:
    """Build a CorrelationTableModel from a list of fund dicts."""
    names, tickers, corr = fetch_correlation_matrix(funds)
    n = len(names)

    abbrevs = _make_abbreviations(names)
    col_headers = ["Fund Name"] + abbrevs

    rows = []
    for name in names:
        row = [name] + [_fmt(corr.loc[name, other]) for other in names]
        rows.append(row)

    categories = [f["category"] for f in funds]
    abbrev_key = list(zip(abbrevs, names))

    return CorrelationTableModel(
        col_headers=col_headers,
        rows=rows,
        categories=categories,
        period=PERIOD,
        n_funds=n,
        abbrev_key=abbrev_key,
    )


def main(renderer: CorrelationTableRenderer):
    print("Fetching fund data for correlation matrix...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund inter-fund correlation matrix")
    args = parser.parse_args()

    from GUI.Bokeh.fund_correlation_table_bokeh import BokehCorrelationTableRenderer
    main(BokehCorrelationTableRenderer())
