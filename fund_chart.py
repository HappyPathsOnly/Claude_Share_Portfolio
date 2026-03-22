"""
Dodge & Cox Worldwide Global Stock Fund GBP Acc - Price Chart
ISIN: IE00B54J6879 | Yahoo Finance ticker: 0P0000POWH.L
"""

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.widgets import Button

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
    """Fetch historical closing prices from Yahoo Finance (cached)."""
    if period in _cache:
        return _cache[period]
    fund = yf.Ticker(TICKER)
    df = fund.history(period=period)
    if df.empty:
        raise ValueError(f"No data returned for ticker {TICKER!r}")
    # Yahoo Finance returns prices in GBP; convert to pence (GBX)
    df = df[["Close"]].rename(columns={"Close": "Price (p)"})
    df["Price (p)"] = df["Price (p)"] * 100
    _cache[period] = df
    return df


def draw(ax, df, period_label: str):
    """Redraw the chart on the given axes."""
    ax.clear()
    ax.plot(df.index, df["Price (p)"], linewidth=1.8, color="#0057a8")
    ax.fill_between(df.index, df["Price (p)"], alpha=0.10, color="#0057a8")

    latest_price = df["Price (p)"].iloc[-1]
    start_price = df["Price (p)"].iloc[0]
    change_pct = (latest_price - start_price) / start_price * 100
    sign = "+" if change_pct >= 0 else ""

    ax.set_title(
        f"{FUND_NAME}  |  {period_label} return: {sign}{change_pct:.2f}%",
        fontsize=13, pad=10,
    )
    ax.set_ylabel("Price (pence)", fontsize=11)
    ax.set_xlabel("")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.figure.autofmt_xdate(rotation=30, ha="right")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}p"))
    # Tight y-axis: pad by 5% of the data range so changes are obvious
    price_min = df["Price (p)"].min()
    price_max = df["Price (p)"].max()
    margin = (price_max - price_min) * 0.05
    ax.set_ylim(price_min - margin, price_max + margin)

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)

    # Annotate latest price
    ax.annotate(
        f"  {latest_price:,.2f}p",
        xy=(df.index[-1], latest_price),
        fontsize=10, color="#0057a8", va="center",
    )

    ax.figure.canvas.draw_idle()


def main():
    print(f"Fetching data for {FUND_NAME} ({TICKER})...")

    # Pre-fetch default period
    default_label = "1Y"
    df = fetch_prices(PERIODS[default_label])
    latest = df["Price (p)"].iloc[-1]
    print(f"  Latest price : {latest:,.2f}p  ({df.index[-1].date()})")

    # Build figure — leave room at the bottom for buttons
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_axes([0.07, 0.18, 0.90, 0.72])  # [left, bottom, width, height]
    draw(ax, df, default_label)

    # --- Period buttons ---
    period_labels = list(PERIODS.keys())
    n = len(period_labels)
    btn_width = 0.09
    btn_height = 0.06
    gap = 0.01
    total_width = n * btn_width + (n - 1) * gap
    x_start = (1.0 - total_width) / 2

    buttons = []
    active_label = [default_label]  # mutable container so closure can update it

    def make_callback(label):
        def on_click(_event):
            if label == active_label[0]:
                return
            active_label[0] = label
            print(f"  Loading {label}...")
            new_df = fetch_prices(PERIODS[label])
            draw(ax, new_df, label)
            # Update button colours
            for btn, lbl in zip(buttons, period_labels):
                btn.color = "#0057a8" if lbl == label else "#e0e8f5"
                btn.hovercolor = "#003d7a" if lbl == label else "#c5d5ea"
                btn.label.set_color("white" if lbl == label else "#0057a8")
            fig.canvas.draw_idle()
        return on_click

    for i, label in enumerate(period_labels):
        x = x_start + i * (btn_width + gap)
        btn_ax = fig.add_axes([x, 0.04, btn_width, btn_height])
        is_active = label == default_label
        btn = Button(
            btn_ax, label,
            color="#0057a8" if is_active else "#e0e8f5",
            hovercolor="#003d7a" if is_active else "#c5d5ea",
        )
        btn.label.set_color("white" if is_active else "#0057a8")
        btn.label.set_fontsize(10)
        btn.on_clicked(make_callback(label))
        buttons.append(btn)

    plt.show()


if __name__ == "__main__":
    main()
