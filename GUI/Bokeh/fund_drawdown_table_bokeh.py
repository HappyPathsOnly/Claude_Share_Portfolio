"""
Bokeh renderer for the fund max-drawdown table.

Max drawdown (MDD) is the worst peak-to-trough decline over a period, expressed as a
negative percentage.  For example, -25% means the fund fell 25% from its highest point
to its lowest point before recovering.  It is a measure of downside risk: a larger
negative value indicates the fund has historically suffered steeper losses.

Drawdown cells are heat-mapped: green (< 5%), amber (5–20%), red (> 20%).
Values are negative percentages so thresholds compare absolute values.
"""

import sys
import os

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
        "Missing dependency: bokeh is required. Install it with: pip install bokeh"
    ) from exc

from fund_drawdown_table_renderer import DrawdownTableModel, DrawdownTableRenderer
from utils.fund_constants import ROW_FG, GREEN, RED
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)

_AMBER = "#c97a00"


def _drawdown_color(text: str) -> str:
    """Return a heat-map CSS colour for a drawdown string like '-14.32%'."""
    try:
        val = abs(float(text.rstrip("%")))
    except ValueError:
        return ROW_FG
    if val < 5.0:
        return GREEN
    if val < 20.0:
        return _AMBER
    return RED


def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    total_row: list[str],
    dd_col_indices: set[int],
    categories: list[str] | None = None,
) -> tuple[ColumnDataSource, list[TableColumn], int]:
    keys = [f"c{i}" for i in range(len(headers))]
    color_keys = {i: f"dd_color_{i}" for i in dd_col_indices}

    source_data: dict[str, list] = {k: [] for k in keys}
    for ck in color_keys.values():
        source_data[ck] = []
    source_data["row_style"] = []

    n_separators = 0
    display_row = 0
    for i, row in enumerate(data_rows):
        if categories and i > 0 and categories[i] != categories[i - 1]:
            for k in keys:
                source_data[k].append("")
            for ck in color_keys.values():
                source_data[ck].append(ROW_FG)
            source_data["row_style"].append(SEP_STYLE)
            n_separators += 1

        for k, v in zip(keys, row):
            source_data[k].append(v)
        for col_idx, ck in color_keys.items():
            source_data[ck].append(_drawdown_color(row[col_idx]))
        source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
        display_row += 1

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    for col_idx, ck in color_keys.items():
        source_data[ck].append(_drawdown_color(total_row[col_idx]))
    source_data["row_style"].append(TOTAL_STYLE)

    source = ColumnDataSource(source_data)

    table_cols = []
    for i, h in enumerate(headers):
        if i in dd_col_indices:
            tmpl = (
                f'<div style="<%= row_style %>; color: <%= dd_color_{i} %>; '
                f'height: 100%; padding: 4px 10px; overflow: hidden; '
                f'text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">'
                f'<%= value %></div>'
            )
            fmt = HTMLTemplateFormatter(template=tmpl)
        else:
            fmt = HTMLTemplateFormatter(template=CELL_TEMPLATE)
        table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt))

    return source, table_cols, n_separators


class BokehDrawdownTableRenderer(DrawdownTableRenderer):
    def render(self, model: DrawdownTableModel, output_path: str | None = None) -> None:
        main_dd_cols = set(range(2, len(model.col_headers)))
        main_source, main_cols, main_seps = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row,
            dd_col_indices=main_dd_cols,
            categories=model.categories,
        )
        main_table = DataTable(
            source=main_source,
            columns=main_cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.rows), main_seps),
            width=1000,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        date_source, date_cols, date_seps = _build_source_and_columns(
            model.date_col_headers, model.date_rows, [""] * len(model.date_col_headers),
            dd_col_indices=set(),
            categories=model.categories,
        )
        date_table = DataTable(
            source=date_source,
            columns=date_cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.date_rows), date_seps),
            width=1000,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        layout = column(
            page_css_div(),
            make_title_div("Fund Portfolio \u2013 Max Drawdown", 1000),
            main_table,
            make_title_div("Fund Portfolio \u2013 Trough Dates", 1000),
            date_table,
        )
        if output_path:
            from bokeh.io import output_file, save
            output_file(output_path)
            save(layout)
        else:
            show(layout)
