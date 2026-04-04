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
    from bokeh.models import (
        ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter, Div,
        InlineStyleSheet,
    )
    from bokeh.layouts import column
    from bokeh.io import show
except ImportError as exc:
    raise ImportError(
        "Missing dependency: bokeh is required to run fund_change_table_bokeh. "
        "Install it with: pip install bokeh"
    ) from exc

from fund_table_renderer import TableModel, TableRenderer
from fund_constants import HEADER_BG, TOTAL_BG, TOTAL_FG, ROW_BG_ODD, ROW_BG_EVEN, ROW_FG, GREEN, RED

# Column indices that contain percentage-change values and need green/red colouring.
_PCT_COLS = {3, 4, 5, 6, 7}

_ROW_H    = 30    # px per data row
_HEADER_H = 32    # px for the header row

# Injected into the shadow DOM of the DataTable via stylesheets=.
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

# Light-DOM CSS: only body-level styles.
_PAGE_CSS = """
<style>
  body {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 16px;
  }
</style>
"""

# Separator row style — matches page background so it reads as a blank gap.
_SEP_STYLE = "background-color: #f0f4f8; pointer-events: none;"

# Base cell template — height:100% covers the SlickGrid row background completely.
_BASE_TEMPLATE = """
<div style="<%= row_style %>; height: 100%; padding: 4px 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">
  <%= value %>
</div>
"""


def _pct_template(color_key: str) -> str:
    """Cell template for a percentage column: also applies a per-cell text colour."""
    return (
        f'<div style="<%= row_style %>; color: <%= {color_key} %>; '
        f'height: 100%; padding: 4px 10px; overflow: hidden; text-overflow: ellipsis; '
        f'white-space: nowrap; box-sizing: border-box;">'
        f"<%= value %></div>"
    )


def _pct_color(text: str) -> str:
    """Return the CSS colour for a percentage-change string."""
    if text.startswith("+"):
        return GREEN
    if text.startswith("-"):
        return RED
    return ROW_FG


def _table_height(n_data_rows: int, n_separators: int = 0) -> int:
    """Height in px to show all rows without a scrollbar."""
    return _HEADER_H + (n_data_rows + 1 + n_separators) * _ROW_H + 8


class BokehChangeTableRenderer(TableRenderer):
    def render(self, model: TableModel) -> None:
        n_cols = len(model.col_headers)
        keys = [f"c{i}" for i in range(n_cols)]
        color_keys = {i: f"c{i}_color" for i in _PCT_COLS}

        source_data: dict[str, list] = {k: [] for k in keys}
        for ck in color_keys.values():
            source_data[ck] = []
        source_data["row_style"] = []

        total_style = f"font-weight: 700; background-color: {TOTAL_BG}; color: {TOTAL_FG}; font-size: 13px;"
        odd_style   = f"background-color: {ROW_BG_ODD};  color: {ROW_FG};"
        even_style  = f"background-color: {ROW_BG_EVEN}; color: {ROW_FG};"

        n_separators = 0
        display_row  = 0
        for i, row in enumerate(model.rows):
            # Blank separator row between categories
            if i > 0 and model.categories[i] != model.categories[i - 1]:
                for k in keys:
                    source_data[k].append("")
                for ck in color_keys.values():
                    source_data[ck].append(ROW_FG)
                source_data["row_style"].append(_SEP_STYLE)
                n_separators += 1

            for k, v in zip(keys, row):
                source_data[k].append(v)
            for col_idx, ck in color_keys.items():
                source_data[ck].append(_pct_color(row[col_idx]))
            source_data["row_style"].append(odd_style if display_row % 2 == 0 else even_style)
            display_row += 1

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
            height=_table_height(len(model.rows), n_separators),
            width=1380,
            sizing_mode="fixed",
            stylesheets=[InlineStyleSheet(css=_TABLE_CSS)],
        )

        page_css = Div(text=_PAGE_CSS)
        title = Div(
            text=(
                f'<div style="width:1380px;">'
                f'<div style="background:linear-gradient(180deg,{HEADER_BG} 0%,#003d7a 100%); '
                f'padding:10px 16px; border-radius:4px 4px 0 0; text-align:center;">'
                f'<span style="color:white; font-family:\'Segoe UI\',Arial,sans-serif; '
                f'font-size:14px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">'
                f'Fund Portfolio \u2013 Percentage Change</span></div></div>'
            )
        )

        show(column(page_css, title, table))
