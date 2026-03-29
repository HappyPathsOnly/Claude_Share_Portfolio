"""
Shared matplotlib helpers for fund table renderers.
"""

import matplotlib.pyplot as plt
from fund_constants import CELL_PADDING, FONT_SIZE, BORDER_WIDTH, BORDER, TABLE_LEFT


def draw_cell(ax, x, y, w, h, text, bg, fg, align, fontsize=FONT_SIZE, bold=False):
    """Draw a single table cell (background rectangle + text) on the given axes."""
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


def compute_x_positions(col_widths: list[float], start_x: float = TABLE_LEFT) -> list[float]:
    """Return the left x-coordinate of each column given a list of column widths."""
    positions = []
    x = start_x
    for w in col_widths:
        positions.append(x)
        x += w
    return positions
