"""
Fund Portfolio - Percentage Change Table
Shows percentage change in fund value over various time periods relative to current value.
"""

import matplotlib.pyplot as plt
from fund_utils import CSV_PATH, load_funds, fetch_prices_gbp


def pct_change(current, past) -> str:
    """Format percentage change from past to current."""
    change = (current - past) / past * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%"


def build_rows(funds: list) -> tuple[list, list]:
    """Return (rows, totals). totals = [total_now, total_1w, total_1m, total_6m, total_1y]."""
    rows = []
    totals = [0.0, 0.0, 0.0, 0.0, 0.0]
    for f in funds:
        prices = fetch_prices_gbp(f["ticker"])
        price_now, price_1w, price_1m, price_6m, price_1y = prices
        values = [p * f["units"] for p in prices]
        for i, v in enumerate(values):
            totals[i] += v
        rows.append([
            f["name"],
            f["ticker"],
            f"{f['units']:,}",
            pct_change(price_now, price_1y),
            pct_change(price_now, price_6m),
            pct_change(price_now, price_1m),
            pct_change(price_now, price_1w),
            f"£{values[0]:,.2f}",
        ])
    return rows, totals


def main():
    print("Fetching fund data...")
    funds = load_funds(CSV_PATH)
    rows, totals = build_rows(funds)
    total_now, total_1w, total_1m, total_6m, total_1y = totals

    total_row = [
        "", "", "Total",
        pct_change(total_now, total_1y),
        pct_change(total_now, total_6m),
        pct_change(total_now, total_1m),
        pct_change(total_now, total_1w),
        f"£{total_now:,.2f}",
    ]

    col_headers = ["Fund Name", "Ticker", "Units", "1Y Change", "6M Change", "1M Change", "1W Change", "Value"]

    fig, ax = plt.subplots(figsize=(18, max(2.5, 0.5 + 0.4 * (len(rows) + 2))))
    ax.axis("off")

    table_data = [col_headers] + rows + [total_row]

    n_cols = len(col_headers)
    n_rows = len(table_data)

    col_widths = [0.24, 0.10, 0.07, 0.11, 0.11, 0.11, 0.11, 0.11]
    col_aligns = ["left", "center", "right", "right", "right", "right", "right", "right"]

    row_height = 0.12
    header_height = 0.14
    table_top = 0.92

    HEADER_BG   = "#0057a8"
    HEADER_FG   = "white"
    ROW_BG_ODD  = "#f5f8fd"
    ROW_BG_EVEN = "white"
    TOTAL_BG    = "#dce8f7"
    BORDER      = "#b0c4de"
    GREEN       = "#1a7a3a"
    RED         = "#b22222"

    x_positions = []
    x = 0.03
    for w in col_widths:
        x_positions.append(x)
        x += w

    def draw_cell(ax, x, y, w, h, text, bg, fg, align, fontsize=10, bold=False):
        rect = plt.Rectangle((x, y), w, h, transform=ax.transAxes,
                              color=bg, zorder=1, clip_on=False,
                              linewidth=0.8, edgecolor=BORDER)
        ax.add_patch(rect)
        if align == "left":
            tx, ha = x + 0.01, "left"
        elif align == "right":
            tx, ha = x + w - 0.01, "right"
        else:
            tx, ha = x + w / 2, "center"
        ax.text(tx, y + h / 2, text, transform=ax.transAxes,
                ha=ha, va="center", fontsize=fontsize,
                color=fg, fontweight="bold" if bold else "normal", zorder=2, clip_on=False)

    for row_idx, row_data in enumerate(table_data):
        is_header = row_idx == 0
        is_total  = row_idx == n_rows - 1
        if is_header:
            bg, base_fg = HEADER_BG, HEADER_FG
        elif is_total:
            bg, base_fg = TOTAL_BG, "#003d7a"
        else:
            bg, base_fg = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), "#1a1a2e"
        h = header_height if is_header else row_height

        if row_idx == 0:
            y = table_top - header_height
        else:
            y = table_top - header_height - row_idx * row_height

        for col_idx in range(n_cols):
            text = row_data[col_idx]
            # Colour percentage change columns green/red
            if not is_header and col_idx in (3, 4, 5, 6):
                fg = GREEN if text.startswith("+") else RED
            else:
                fg = base_fg
            draw_cell(ax, x_positions[col_idx], y, col_widths[col_idx], h,
                      text, bg, fg, col_aligns[col_idx],
                      fontsize=10, bold=(is_header or is_total))

    fig.suptitle("Fund Portfolio - Percentage Change", fontsize=14, fontweight="bold",
                 color="#0057a8", y=0.98)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
