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

from bokeh.models import (
    ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter, Div,
    InlineStyleSheet,
)
from bokeh.layouts import column
from bokeh.io import show

from fund_value_table_renderer import ValueTableModel, ValueTableRenderer
from fund_constants import HEADER_BG, TOTAL_BG, TOTAL_FG, ROW_BG_ODD, ROW_BG_EVEN, ROW_FG

# Cell template: per-row inline style comes from the `row_style` source column.
# height:100% ensures the div covers the full SlickGrid row background.
_CELL_TEMPLATE = """
<div style="<%= row_style %>; height: 100%; padding: 4px 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">
  <%= value %>
</div>
"""

# Injected into the shadow DOM of each DataTable via stylesheets=.
# This is the only reliable way to reach SlickGrid internals in Bokeh 3.x.
_TABLE_CSS = f"""
  .slick-header-columns {{
    background: {HEADER_BG} !important;
  }}
  .slick-header-column {{
    background: linear-gradient(180deg, {HEADER_BG} 0%, #003d7a 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-right: 1px solid rgba(255,255,255,0.2) !important;
  }}
  .slick-header-column:hover {{
    background: linear-gradient(180deg, #1a6fc4 0%, #004f9a 100%) !important;
  }}
  .slick-cell {{
    border-right: 1px solid #b0c4de !important;
    border-bottom: 1px solid #b0c4de !important;
    box-sizing: border-box;
  }}
  .slick-row {{
    border-left: 1px solid #b0c4de !important;
  }}
  :host {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: {ROW_FG};
    border: 1px solid #b0c4de;
  }}
"""

# Light-DOM CSS: only body-level styles that don't need shadow-DOM access.
_PAGE_CSS = """
<style>
  body {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 16px;
  }
</style>
"""

_ROW_H = 30       # px per data row
_HEADER_H = 32    # px for the header row


def _make_stylesheet() -> InlineStyleSheet:
    """Return a fresh InlineStyleSheet instance (each widget needs its own)."""
    return InlineStyleSheet(css=_TABLE_CSS)


_SEP_STYLE = "background-color: #f0f4f8; pointer-events: none;"

def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    total_row: list[str],
    categories: list[str] | None = None,
) -> tuple[ColumnDataSource, list[TableColumn], int]:
    """Pack rows + total into a ColumnDataSource and return (source, columns, n_separators)."""
    keys = [f"c{i}" for i in range(len(headers))]

    source_data: dict[str, list] = {k: [] for k in keys}
    source_data["row_style"] = []

    total_style = f"font-weight: 700; background-color: {TOTAL_BG}; color: {TOTAL_FG}; font-size: 13px;"
    odd_style   = f"background-color: {ROW_BG_ODD};  color: {ROW_FG};"
    even_style  = f"background-color: {ROW_BG_EVEN}; color: {ROW_FG};"

    n_separators = 0
    display_row = 0   # counts only real rows, so alternating colours ignore separators
    for i, row in enumerate(data_rows):
        # Insert a blank separator row when the category changes (skip before first row)
        if categories and i > 0 and categories[i] != categories[i - 1]:
            for k in keys:
                source_data[k].append("")
            source_data["row_style"].append(_SEP_STYLE)
            n_separators += 1

        for k, v in zip(keys, row):
            source_data[k].append(v)
        source_data["row_style"].append(odd_style if display_row % 2 == 0 else even_style)
        display_row += 1

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    source_data["row_style"].append(total_style)

    source = ColumnDataSource(source_data)

    table_cols = [
        TableColumn(field=k, title=h, formatter=HTMLTemplateFormatter(template=_CELL_TEMPLATE))
        for k, h in zip(keys, headers)
    ]
    return source, table_cols, n_separators


def _table_height(n_data_rows: int, n_separators: int = 0) -> int:
    """Height in px to show all rows without a scrollbar."""
    return _HEADER_H + (n_data_rows + 1 + n_separators) * _ROW_H + 8


class BokehValueTableRenderer(ValueTableRenderer):
    def render(self, model: ValueTableModel) -> None:
        # --- Main fund table ---
        main_source, main_cols, main_seps = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row, categories=model.categories
        )
        main_table = DataTable(
            source=main_source,
            columns=main_cols,
            index_position=None,
            header_row=True,
            row_height=_ROW_H,
            height=_table_height(len(model.rows), main_seps),
            width=1380,
            sizing_mode="fixed",
            stylesheets=[_make_stylesheet()],
        )

        # --- Category summary table ---
        cat_source, cat_cols, _ = _build_source_and_columns(
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
            stylesheets=[_make_stylesheet()],
        )

        page_css = Div(text=_PAGE_CSS)
        title = Div(
            text=(
                f'<div style="width:1380px;">'
                f'<div style="background:linear-gradient(180deg,{HEADER_BG} 0%,#003d7a 100%); '
                f'padding:10px 16px; border-radius:4px 4px 0 0; text-align:center;">'
                f'<span style="color:white; font-family:\'Segoe UI\',Arial,sans-serif; '
                f'font-size:14px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">'
                f'Fund Portfolio</span></div></div>'
            )
        )
        cat_title = Div(
            text=(
                f'<div style="width:870px; margin-top:24px;">'
                f'<div style="background:linear-gradient(180deg,{HEADER_BG} 0%,#003d7a 100%); '
                f'padding:10px 16px; border-radius:4px 4px 0 0; text-align:center;">'
                f'<span style="color:white; font-family:\'Segoe UI\',Arial,sans-serif; '
                f'font-size:14px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">'
                f'By Category</span></div></div>'
            )
        )

        show(column(page_css, title, main_table, cat_title, cat_table))
