"""
Dodge & Cox Worldwide Global Stock Fund GBP Acc - Price Chart
ISIN: IE00B54J6879 | Yahoo Finance ticker: 0P0000POWH.L
"""

import yfinance as yf
from fund_chart_renderer import ChartModel, ChartRenderer

TICKER = "0P0000POWH.L"
FUND_NAME = "Dodge & Cox Worldwide Global Stock Fund GBP Acc"
PERIODS = {
    "1M":  "1mo",
    "3M":  "3mo",
    "6M":  "6mo",
    "1Y":  "1y",
    "3Y":  "3y",
    "5Y":  "5y",
    "10Y": "10y",
}

# Cache fetched data to avoid re-downloading the same period
_cache: dict = {}


def fetch_prices(period: str) -> "pd.DataFrame":
    """Fetch historical closing prices from Yahoo Finance (cached). period is a yfinance period string."""
    if period in _cache:
        return _cache[period]
    fund = yf.Ticker(TICKER)
    df = fund.history(period=period)
    if df.empty:
        raise ValueError(f"No data returned for ticker {TICKER!r}")
    df = df[["Close"]].rename(columns={"Close": "Price (p)"})
    df["Price (p)"] = df["Price (p)"] * 100
    _cache[period] = df
    return df


def build_chart_model(default_label: str = "1Y") -> ChartModel:
    """Fetch the default period and build a ChartModel ready for rendering."""
    df = fetch_prices(PERIODS[default_label])
    return ChartModel(
        df=df,
        period_label=default_label,
        fund_name=FUND_NAME,
        period_labels=list(PERIODS.keys()),
        fetch_fn=lambda label: fetch_prices(PERIODS[label]),
    )


def main(renderer: ChartRenderer):
    print(f"Fetching data for {FUND_NAME} ({TICKER})...")
    model = build_chart_model()
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund price chart")
    parser.add_argument("--bokeh", action="store_true", help="Use Bokeh renderer (opens in browser)")
    args = parser.parse_args()

    if args.bokeh:
        from GUI.Bokeh.fund_chart_bokeh import BokehChartRenderer
        main(BokehChartRenderer())
    else:
        from fund_chart_matplotlib import MatplotlibChartRenderer
        main(MatplotlibChartRenderer())
