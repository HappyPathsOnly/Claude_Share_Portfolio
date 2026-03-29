"""
Matplotlib renderer for the fund change table.
"""

import matplotlib.pyplot as plt
from fund_table_renderer import TableModel, TableRenderer
from fund_constants import (
    HEADER_BG, HEADER_FG, ROW_BG_ODD, ROW_BG_EVEN, TOTAL_BG, TOTAL_FG,
    BORDER, ROW_FG, GREEN, RED, TABLE_TOP, TABLE_LEFT,
    CELL_PADDING, FONT_SIZE, TITLE_FONT_SIZE, BORDER_WIDTH,
)


class MatplotlibTableRenderer(TableRenderer):
    def render(self, model: TableModel) -> None:
        col_headers = model.col_headers
        rows = model.rows
        total_row = model.total_row
        categories = model.categories

        n_unique_cats = len(set(categories))
        n_gaps = max(0, n_unique_cats - 1)
        table_data = [col_headers] + rows + [total_row]
        n_cols = len(col_headers)
        n_rows = len(table_data)

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
