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
_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    from bokeh.models import ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter
    from bokeh.layouts import column
    from bokeh.io import show
except ImportError as exc:
    raise ImportError(
        "Missing dependency: bokeh is required to run fund_change_table_bokeh. "
        "Install it with: pip install bokeh"
    ) from exc

from fund_table_renderer import TableModel, TableRenderer
from fund_constants import ROW_FG, GREEN, RED
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)

# Column indices that contain percentage-change values and need green/red colouring.
_PCT_COLS = {3, 4, 5, 6, 7}


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


class BokehChangeTableRenderer(TableRenderer):
    def render(self, model: TableModel) -> None:
        n_cols = len(model.col_headers)
        keys = [f"c{i}" for i in range(n_cols)]
        color_keys = {i: f"c{i}_color" for i in _PCT_COLS}

        source_data: dict[str, list] = {k: [] for k in keys}
        for ck in color_keys.values():
            source_data[ck] = []
        source_data["row_style"] = []

        n_separators = 0
        display_row  = 0
        for i, row in enumerate(model.rows):
            # Blank separator row between categories
            if i > 0 and model.categories[i] != model.categories[i - 1]:
                for k in keys:
                    source_data[k].append("")
                for ck in color_keys.values():
                    source_data[ck].append(ROW_FG)
                source_data["row_style"].append(SEP_STYLE)
                n_separators += 1

            for k, v in zip(keys, row):
                source_data[k].append(v)
            for col_idx, ck in color_keys.items():
                source_data[ck].append(_pct_color(row[col_idx]))
            source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
            display_row += 1

        # Total row — percentage cells still get green/red
        for k, v in zip(keys, model.total_row):
            source_data[k].append(v)
        for col_idx, ck in color_keys.items():
            source_data[ck].append(_pct_color(model.total_row[col_idx]))
        source_data["row_style"].append(TOTAL_STYLE)

        source = ColumnDataSource(source_data)

        table_cols = []
        for i, h in enumerate(model.col_headers):
            if i in _PCT_COLS:
                fmt = HTMLTemplateFormatter(template=_pct_template(color_keys[i]))
            else:
                fmt = HTMLTemplateFormatter(template=CELL_TEMPLATE)
            table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt))

        table = DataTable(
            source=source,
            columns=table_cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.rows), n_separators),
            width=1380,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        show(column(
            page_css_div(),
            make_title_div("Fund Portfolio \u2013 Percentage Change", 1380),
            table,
        ))
