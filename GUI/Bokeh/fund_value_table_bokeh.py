"""
Bokeh renderer for the fund value table.
Opens the tables in a browser tab.
"""

import sys
import os

# Ensure the project root is on sys.path so shared modules are importable
# regardless of where this file is invoked from.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bokeh.models import ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter, Div
from bokeh.layouts import column
from bokeh.io import show

from fund_value_table_renderer import ValueTableModel, ValueTableRenderer
from fund_constants import HEADER_BG, TOTAL_BG, TOTAL_FG

# Cell template: applies per-row style stored in the `row_style` source column.
_CELL_TEMPLATE = """
<div style="<%= row_style %>; padding: 2px 6px; overflow: hidden; text-overflow: ellipsis;">
  <%= value %>
</div>
"""

# Injected CSS: styles the DataTable header rows to match the project palette.
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

_ROW_H = 28       # px per data row
_HEADER_H = 30    # px for the header row


def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    total_row: list[str],
) -> tuple[ColumnDataSource, list[TableColumn]]:
    """Pack rows + total into a ColumnDataSource and return paired TableColumn list."""
    keys = [f"c{i}" for i in range(len(headers))]

    source_data: dict[str, list] = {k: [] for k in keys}
    source_data["row_style"] = []

    normal_style = ""
    total_style = f"font-weight: bold; background-color: {TOTAL_BG}; color: {TOTAL_FG};"

    for row in data_rows:
        for k, v in zip(keys, row):
            source_data[k].append(v)
        source_data["row_style"].append(normal_style)

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    source_data["row_style"].append(total_style)

    source = ColumnDataSource(source_data)

    table_cols = [
        TableColumn(field=k, title=h, formatter=HTMLTemplateFormatter(template=_CELL_TEMPLATE))
        for k, h in zip(keys, headers)
    ]
    return source, table_cols


def _table_height(n_data_rows: int) -> int:
    """Height in px to show all rows without a scrollbar."""
    return _HEADER_H + (n_data_rows + 1) * _ROW_H + 8   # +1 for total row, 8px buffer


class BokehValueTableRenderer(ValueTableRenderer):
    def render(self, model: ValueTableModel) -> None:
        # --- Main fund table ---
        main_source, main_cols = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row
        )
        main_table = DataTable(
            source=main_source,
            columns=main_cols,
            index_position=None,
            header_row=True,
            row_height=_ROW_H,
            height=_table_height(len(model.rows)),
            width=1380,
            sizing_mode="fixed",
        )

        # --- Category summary table ---
        cat_source, cat_cols = _build_source_and_columns(
            model.cat_col_headers, model.cat_data_rows, model.cat_total_row
        )
        cat_table = DataTable(
            source=cat_source,
            columns=cat_cols,
            index_position=None,
            header_row=True,
            row_height=_ROW_H,
            height=_table_height(len(model.cat_data_rows)),
            width=870,
            sizing_mode="fixed",
        )

        css = Div(text=_HEADER_CSS)
        title = Div(
            text=f'<h2 style="color:{HEADER_BG}; font-family:sans-serif; margin:8px 0 4px 0;">'
                 "Fund Portfolio</h2>"
        )
        cat_title = Div(
            text=f'<h3 style="color:{HEADER_BG}; font-family:sans-serif; margin:16px 0 4px 0;">'
                 "By Category</h3>"
        )

        show(column(css, title, main_table, cat_title, cat_table))
