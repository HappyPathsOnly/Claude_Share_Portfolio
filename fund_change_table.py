"""
Fund Portfolio - Percentage Change Table
Shows percentage change in fund value over various time periods relative to current value.
"""

import matplotlib.pyplot as plt
from fund_utils import CSV_PATH, load_funds, fetch_prices_gbp
from fund_constants import (
    HEADER_BG, HEADER_FG, ROW_BG_ODD, ROW_BG_EVEN, TOTAL_BG, TOTAL_FG,
    BORDER, ROW_FG, GREEN, RED, ROW_HEIGHT, HEADER_HEIGHT, TABLE_TOP, TABLE_LEFT,
    CELL_PADDING, FONT_SIZE, TITLE_FONT_SIZE, BORDER_WIDTH,
)


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

    x_positions = []
    x = TABLE_LEFT
    for w in col_widths:
        x_positions.append(x)
        x += w

    def draw_cell(ax, x, y, w, h, text, bg, fg, align, fontsize=FONT_SIZE, bold=False):
        rect = plt.Rectangle((x, y), w, h, transform=ax.transAxes,
                              color=bg, zorder=1, clip_on=False,
                              linewidth=BORDER_WIDTH, edgecolor=BORDER)
        ax.add_patch(rect)
        if align == "left":
            tx, ha = x + CELL_PADDING, "left"
        elif align == "right":
            tx, ha = x + w - CELL_PADDING, "right"
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
            bg, base_fg = TOTAL_BG, TOTAL_FG
        else:
            bg, base_fg = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), ROW_FG
        h = HEADER_HEIGHT if is_header else ROW_HEIGHT

        if row_idx == 0:
            y = TABLE_TOP - HEADER_HEIGHT
        else:
            y = TABLE_TOP - HEADER_HEIGHT - row_idx * ROW_HEIGHT

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

    fig.suptitle("Fund Portfolio - Percentage Change", fontsize=TITLE_FONT_SIZE, fontweight="bold",
                 color=HEADER_BG, y=0.98)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
