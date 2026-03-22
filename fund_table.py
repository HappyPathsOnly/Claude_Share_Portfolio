"""
Fund Portfolio - Value Table
Displays current fund values in a tabular format.
"""

import matplotlib.pyplot as plt
from fund_utils import CSV_PATH, load_funds, fetch_prices_gbp
from fund_constants import (
    HEADER_BG, HEADER_FG, ROW_BG_ODD, ROW_BG_EVEN, TOTAL_BG, TOTAL_FG,
    BORDER, ROW_FG, ROW_HEIGHT, HEADER_HEIGHT, TABLE_TOP, TABLE_LEFT,
    CELL_PADDING, FONT_SIZE, TITLE_FONT_SIZE, BORDER_WIDTH,
)


def build_rows(funds: list) -> tuple[list, float, float, float, float, float, float]:
    """Return (rows, total_now, total_prev, total_1w, total_1m, total_6m, total_1y)."""
    rows = []
    totals = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for f in funds:
        prices = fetch_prices_gbp(f["ticker"])
        values = [p * f["units"] for p in prices]
        for i, v in enumerate(values):
            totals[i] += v
        rows.append([
            f["name"],
            f["ticker"],
            f"{f['units']:,}",
            f"£{values[5]:,.2f}",
            f"£{values[4]:,.2f}",
            f"£{values[3]:,.2f}",
            f"£{values[2]:,.2f}",
            f"£{values[1]:,.2f}",
            f"£{values[0]:,.2f}",
        ])
    return rows, *totals


def main():
    print("Fetching fund data...")
    funds = load_funds(CSV_PATH)
    rows, total_now, total_prev, total_1w, total_1m, total_6m, total_1y = build_rows(funds)

    col_headers = ["Fund Name", "Ticker", "Units", "Value (1Y ago)", "Value (6M ago)", "Value (1M ago)", "Value (1W ago)", "Prev Day", "Value"]

    fig, ax = plt.subplots(figsize=(20, max(2.5, 0.5 + 0.4 * (len(rows) + 2))))
    ax.axis("off")

    # Build table data: header + data rows + total row
    table_data = [col_headers] + rows + [[
        "", "", "Total",
        f"£{total_1y:,.2f}", f"£{total_6m:,.2f}", f"£{total_1m:,.2f}", f"£{total_1w:,.2f}",
        f"£{total_prev:,.2f}", f"£{total_now:,.2f}",
    ]]

    n_cols = len(col_headers)
    n_rows = len(table_data)

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
            tx = x + CELL_PADDING
            ha = "left"
        elif align == "right":
            tx = x + w - CELL_PADDING
            ha = "right"
        else:
            tx = x + w / 2
            ha = "center"
        ax.text(tx, y + h / 2, text, transform=ax.transAxes,
                ha=ha, va="center", fontsize=fontsize,
                color=fg, fontweight="bold" if bold else "normal", zorder=2, clip_on=False)

    for row_idx, row_data in enumerate(table_data):
        is_header = row_idx == 0
        is_total  = row_idx == n_rows - 1

        if is_header:
            bg, fg, h, bold = HEADER_BG, HEADER_FG, HEADER_HEIGHT, True
        elif is_total:
            bg, fg, h, bold = TOTAL_BG, TOTAL_FG, ROW_HEIGHT, True
        else:
            bg, fg, h, bold = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), ROW_FG, ROW_HEIGHT, False

        # y position (top-down)
        if row_idx == 0:
            y = TABLE_TOP - HEADER_HEIGHT
        else:
            y = TABLE_TOP - HEADER_HEIGHT - row_idx * ROW_HEIGHT

        for col_idx in range(n_cols):
            draw_cell(
                ax,
                x_positions[col_idx], y,
                col_widths[col_idx], h,
                row_data[col_idx],
                bg, fg, col_aligns[col_idx],
                fontsize=FONT_SIZE, bold=bold,
            )

    fig.suptitle("Fund Portfolio", fontsize=TITLE_FONT_SIZE, fontweight="bold",
                 color=HEADER_BG, y=0.98)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
