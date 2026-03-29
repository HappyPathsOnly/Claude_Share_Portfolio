"""
Matplotlib renderer for the fund value table.
"""

import matplotlib.pyplot as plt
from fund_value_table_renderer import ValueTableModel, ValueTableRenderer
from fund_constants import (
    HEADER_BG, HEADER_FG, ROW_BG_ODD, ROW_BG_EVEN, TOTAL_BG, TOTAL_FG,
    BORDER, ROW_FG, TABLE_TOP, TABLE_LEFT,
    CELL_PADDING, FONT_SIZE, TITLE_FONT_SIZE, BORDER_WIDTH,
)


class MatplotlibValueTableRenderer(ValueTableRenderer):
    def render(self, model: ValueTableModel) -> None:
        col_headers = model.col_headers
        rows = model.rows
        categories = model.categories

        n_categories = len(model.cat_data_rows)
        n_gaps = max(0, n_categories - 1)
        figheight = max(4.0, 0.5 + 0.4 * (len(rows) + 2) + 0.2 * n_gaps + 0.4 * (n_categories + 3))
        fig, ax = plt.subplots(figsize=(20, figheight))
        ax.set_position([0, 0, 1, 1])
        ax.axis("off")

        table_data = [col_headers] + rows + [model.total_row]
        n_cols = len(col_headers)
        n_rows = len(table_data)

        n_cat_rows_total = n_categories + 2
        row_h = (TABLE_TOP - 0.02) / (n_rows + n_cat_rows_total + 2.4)
        header_h = row_h * 1.2
        gap = row_h * 2.0

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
                bg, fg, h, bold = HEADER_BG, HEADER_FG, header_h, True
            elif is_total:
                bg, fg, h, bold = TOTAL_BG, TOTAL_FG, row_h, True
            else:
                cat = categories[row_idx - 1]
                if prev_cat is not None and cat != prev_cat:
                    current_y -= sep_h
                prev_cat = cat
                bg, fg, h, bold = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), ROW_FG, row_h, False

            current_y -= h
            y = current_y

            for col_idx in range(n_cols):
                draw_cell(ax, x_positions[col_idx], y, col_widths[col_idx], h,
                          row_data[col_idx], bg, fg, col_aligns[col_idx],
                          fontsize=FONT_SIZE, bold=bold)

        main_table_bottom_y = current_y

        # --- Category summary table ---
        cat_col_headers = model.cat_col_headers
        cat_col_widths = [0.22, 0.115, 0.115, 0.115, 0.115, 0.115, 0.115]
        cat_col_aligns = ["left", "right", "right", "right", "right", "right", "right"]

        cat_x_positions = []
        x = TABLE_LEFT
        for w in cat_col_widths:
            cat_x_positions.append(x)
            x += w

        cat_table_data = [cat_col_headers] + model.cat_data_rows + [model.cat_total_row]
        cat_table_top = main_table_bottom_y - gap
        n_cat_rows = len(cat_table_data)
        n_cat_cols = len(cat_col_headers)

        for row_idx, row_data in enumerate(cat_table_data):
            is_header = row_idx == 0
            is_total  = row_idx == n_cat_rows - 1

            if is_header:
                bg, fg, h, bold = HEADER_BG, HEADER_FG, header_h, True
            elif is_total:
                bg, fg, h, bold = TOTAL_BG, TOTAL_FG, row_h, True
            else:
                bg, fg, h, bold = (ROW_BG_ODD if row_idx % 2 == 1 else ROW_BG_EVEN), ROW_FG, row_h, False

            if row_idx == 0:
                y = cat_table_top - header_h
            else:
                y = cat_table_top - header_h - row_idx * row_h

            for col_idx in range(n_cat_cols):
                draw_cell(ax, cat_x_positions[col_idx], y, cat_col_widths[col_idx], h,
                          row_data[col_idx], bg, fg, cat_col_aligns[col_idx],
                          fontsize=FONT_SIZE, bold=bold)

        label_y = cat_table_top + row_h * 0.5
        ax.text(TABLE_LEFT, label_y, "By Category", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=FONT_SIZE + 1,
                color=HEADER_BG, fontweight="bold", zorder=2, clip_on=False)

        fig.suptitle("Fund Portfolio", fontsize=TITLE_FONT_SIZE, fontweight="bold",
                     color=HEADER_BG, y=0.98)

        plt.show()
