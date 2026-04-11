"""
Bokeh renderer for the fund historical volatility table.
Volatility cells are heat-mapped: green (< 10 %), amber (10–20 %), red (> 20 %).
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

from fund_volatility_table_renderer import VolatilityTableModel, VolatilityTableRenderer
from utils.fund_constants import ROW_FG, GREEN, RED
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)

# Amber for medium volatility (10–20 %)
_AMBER = "#c97a00"

# Column indices that hold volatility values and need heat-map colouring.
# Indices 0 and 1 are "Fund Name" and "Ticker".
_VOL_COLS = {2, 3, 4, 5, 6, 7}

_VOL_CELL_TEMPLATE = (
    '<div style="<%= row_style %>; color: <%= vol_color_{i} %>; '
    'height: 100%; padding: 4px 10px; overflow: hidden; text-overflow: ellipsis; '
    'white-space: nowrap; box-sizing: border-box;"><%= value %></div>'
)


def _vol_color(text: str) -> str:
    """Return a heat-map CSS colour for a volatility string like '14.32%'."""
    try:
        val = float(text.rstrip("%"))
    except ValueError:
        return ROW_FG
    if val < 10.0:
        return GREEN
    if val < 20.0:
        return _AMBER
    return RED


def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    total_row: list[str],
    vol_col_indices: set[int],
    categories: list[str] | None = None,
) -> tuple[ColumnDataSource, list[TableColumn], int]:
    keys = [f"c{i}" for i in range(len(headers))]
    color_keys = {i: f"vol_color_{i}" for i in vol_col_indices}

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
            source_data[ck].append(_vol_color(row[col_idx]))
        source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
        display_row += 1

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    for col_idx, ck in color_keys.items():
        source_data[ck].append(_vol_color(total_row[col_idx]))
    source_data["row_style"].append(TOTAL_STYLE)

    source = ColumnDataSource(source_data)

    table_cols = []
    for i, h in enumerate(headers):
        if i in vol_col_indices:
            tmpl = (
                f'<div style="<%= row_style %>; color: <%= vol_color_{i} %>; '
                f'height: 100%; padding: 4px 10px; overflow: hidden; '
                f'text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">'
                f'<%= value %></div>'
            )
            fmt = HTMLTemplateFormatter(template=tmpl)
        else:
            fmt = HTMLTemplateFormatter(template=CELL_TEMPLATE)
        table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt))

    return source, table_cols, n_separators


class BokehVolatilityTableRenderer(VolatilityTableRenderer):
    def render(self, model: VolatilityTableModel, output_path: str | None = None) -> None:
        # Main table: Fund Name, Ticker, vol cols 2–7
        main_vol_cols = set(range(2, len(model.col_headers)))
        main_source, main_cols, main_seps = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row,
            vol_col_indices=main_vol_cols,
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

        # Category summary table: Category, vol cols 1–6
        cat_vol_cols = set(range(1, len(model.cat_col_headers)))
        cat_source, cat_cols, _ = _build_source_and_columns(
            model.cat_col_headers, model.cat_data_rows, model.cat_total_row,
            vol_col_indices=cat_vol_cols,
        )
        cat_table = DataTable(
            source=cat_source,
            columns=cat_cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.cat_data_rows)),
            width=800,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        layout = column(
            page_css_div(),
            make_title_div("Fund Portfolio \u2013 Historical Volatility", 1000),
            main_table,
            make_title_div("By Category", 800),
            cat_table,
        )
        if output_path:
            from bokeh.io import output_file, save
            output_file(output_path)
            save(layout)
        else:
            show(layout)
