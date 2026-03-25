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


def build_rows(funds: list) -> tuple[list, list, list]:
    """Return (rows, totals, categories). totals = [total_now, total_prev, total_1w, total_1m, total_6m, total_1y]."""
    rows = []
    categories = []
    totals = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for f in funds:
        prices = fetch_prices_gbp(f["ticker"])
        price_now, price_prev, price_1w, price_1m, price_6m, price_1y = prices
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
            pct_change(price_now, price_prev),
            f"£{values[0]:,.2f}",
        ])
        categories.append(f["category"])
    return rows, totals, categories


def main():
    print("Fetching fund data...")
    funds = load_funds(CSV_PATH)
    rows, totals, categories = build_rows(funds)
    total_now, total_prev, total_1w, total_1m, total_6m, total_1y = totals

    total_row = [
        "", "", "Total",
        pct_change(total_now, total_1y),
        pct_change(total_now, total_6m),
        pct_change(total_now, total_1m),
        pct_change(total_now, total_1w),
        pct_change(total_now, total_prev),
        f"£{total_now:,.2f}",
    ]

    col_headers = ["Fund Name", "Ticker", "Units", "1Y Change", "6M Change", "1M Change", "1W Change", "Prev Day", "Value"]

    n_unique_cats = len(set(categories))
    n_gaps = max(0, n_unique_cats - 1)
    table_data = [col_headers] + rows + [total_row]
    n_cols = len(col_headers)
    n_rows = len(table_data)

    # Dynamic row height so all rows fit within the figure
    row_h = (TABLE_TOP - 0.02) / (n_rows + 0.2 + n_gaps * 0.5)
    header_h = row_h * 1.2
    figheight = max(2.5, 0.5 + 0.4 * (n_rows + n_gaps * 0.5))
    fig, ax = plt.subplots(figsize=(20, figheight))
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    col_widths = [0.22, 0.09, 0.06, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09]
    col_aligns = ["left", "center", "right", "right", "right", "right", "right", "right", "right"]

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

    sep_h = row_h * 0.5
    current_y = TABLE_TOP
    prev_cat = None

    for row_idx, row_data in enumerate(table_data):
        is_header = row_idx == 0
        is_total  = row_idx == n_rows - 1
        if is_header:
            bg, base_fg, h = HEADER_BG, HEADER_FG, header_h
        elif is_total:
            bg, base_fg, h = TOTAL_BG, TOTAL_FG, row_h
        else:
            cat = categories[row_idx - 1]
            if prev_cat is not None and cat != prev_cat:
                current_y -= sep_h
            prev_cat = cat
            bg, base_fg, h = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), ROW_FG, row_h

        current_y -= h
        y = current_y

        for col_idx in range(n_cols):
            text = row_data[col_idx]
            # Colour percentage change columns green/red
            if not is_header and col_idx in (3, 4, 5, 6, 7):
                fg = GREEN if text.startswith("+") else RED
            else:
                fg = base_fg
            draw_cell(ax, x_positions[col_idx], y, col_widths[col_idx], h,
                      text, bg, fg, col_aligns[col_idx],
                      fontsize=FONT_SIZE, bold=(is_header or is_total))

    fig.suptitle("Fund Portfolio - Percentage Change", fontsize=TITLE_FONT_SIZE, fontweight="bold",
                 color=HEADER_BG, y=0.98)

    plt.show()


if __name__ == "__main__":
    main()
