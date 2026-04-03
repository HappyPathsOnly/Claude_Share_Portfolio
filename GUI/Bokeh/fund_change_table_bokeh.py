"""
Bokeh renderer for the fund percentage-change table.
Opens the table in a browser tab.
"""

import sys
import os

# Ensure the project root is on sys.path so shared modules are importable
# regardless of where this file is invoked from.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

try:
    from bokeh.models import ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter, Div
    from bokeh.layouts import column
    from bokeh.io import show
except ImportError as exc:
    raise ImportError(
        "Missing dependency: bokeh is required to run fund_change_table_bokeh. "
        "Install it with: pip install bokeh"
    ) from exc

from fund_table_renderer import TableModel, TableRenderer
from fund_constants import HEADER_BG, TOTAL_BG, TOTAL_FG, ROW_FG, GREEN, RED

# Column indices that contain percentage-change values and need green/red colouring.
_PCT_COLS = {3, 4, 5, 6, 7}

_ROW_H = 28       # px per data row
_HEADER_H = 30    # px for the header row

# Injected CSS: styles DataTable header rows to match the project palette.
_HEADER_CSS = f"""
<style>
  .slick-header-column {{
    background-color: {HEADER_BG} !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 12px !important;
  }}
  .bk-data-table {{
    font-size: 12px;
    font-family: sans-serif;
  }}
</style>
"""

# Base cell template — uses `row_style` for row-level background/weight.
_BASE_TEMPLATE = """
<div style="<%= row_style %>; padding: 2px 6px; overflow: hidden; text-overflow: ellipsis;">
  <%= value %>
</div>
"""


def _pct_template(color_key: str) -> str:
    """Cell template for a percentage column: also applies a per-cell text colour."""
    return (
        f'<div style="<%= row_style %>; color: <%= {color_key} %>; '
        f'padding: 2px 6px; overflow: hidden; text-overflow: ellipsis;">'
        f"<%= value %></div>"
    )


def _pct_color(text: str) -> str:
    """Return the CSS colour for a percentage-change string."""
    if text.startswith("+"):
        return GREEN
    if text.startswith("-"):
        return RED
    return ROW_FG


def _table_height(n_data_rows: int) -> int:
    """Height in px to show all rows without a scrollbar."""
    return _HEADER_H + (n_data_rows + 1) * _ROW_H + 8   # +1 for total row, 8px buffer


class BokehChangeTableRenderer(TableRenderer):
    def render(self, model: TableModel) -> None:
        n_cols = len(model.col_headers)
        keys = [f"c{i}" for i in range(n_cols)]
        color_keys = {i: f"c{i}_color" for i in _PCT_COLS}

        # Initialise source dict
        source_data: dict[str, list] = {k: [] for k in keys}
        for ck in color_keys.values():
            source_data[ck] = []
        source_data["row_style"] = []

        normal_style = ""
        total_style = f"font-weight: bold; background-color: {TOTAL_BG}; color: {TOTAL_FG};"

        # Data rows
        for row in model.rows:
            for k, v in zip(keys, row):
                source_data[k].append(v)
            for col_idx, ck in color_keys.items():
                source_data[ck].append(_pct_color(row[col_idx]))
            source_data["row_style"].append(normal_style)

        # Total row — percentage cells still get green/red
        for k, v in zip(keys, model.total_row):
            source_data[k].append(v)
        for col_idx, ck in color_keys.items():
            source_data[ck].append(_pct_color(model.total_row[col_idx]))
        source_data["row_style"].append(total_style)

        source = ColumnDataSource(source_data)

        table_cols = []
        for i, h in enumerate(model.col_headers):
            if i in _PCT_COLS:
                fmt = HTMLTemplateFormatter(template=_pct_template(color_keys[i]))
            else:
                fmt = HTMLTemplateFormatter(template=_BASE_TEMPLATE)
            table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt))

        table = DataTable(
            source=source,
            columns=table_cols,
            index_position=None,
            header_row=True,
            row_height=_ROW_H,
            height=_table_height(len(model.rows)),
            width=1380,
            sizing_mode="fixed",
        )

        css = Div(text=_HEADER_CSS)
        title = Div(
            text=f'<h2 style="color:{HEADER_BG}; font-family:sans-serif; margin:8px 0 4px 0;">'
                 "Fund Portfolio &ndash; Percentage Change</h2>"
        )

        show(column(css, title, table))
