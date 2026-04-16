"""
Bokeh renderer for the fund Sharpe ratio table.
Sharpe cells are heat-mapped:
  green  (>= 1.0)  – strong risk-adjusted return
  amber  (0.0–1.0) – modest risk-adjusted return
  red    (< 0.0)   – negative risk-adjusted return
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

from renderers.fund_sharpe_table_renderer import SharpeTableModel, SharpeTableRenderer
from utils.fund_constants import ROW_FG, GREEN, RED
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)

# Amber for moderate Sharpe (0–1)
_AMBER = "#c97a00"


def _sharpe_color(text: str) -> str:
    """Return a heat-map CSS colour for a Sharpe ratio string like '1.23' or '-0.45'."""
    if text in ("N/A", ""):
        return ROW_FG
    try:
        val = float(text)
    except ValueError:
        return ROW_FG
    if val >= 1.0:
        return GREEN
    if val >= 0.0:
        return _AMBER
    return RED


def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    total_row: list[str],
    sharpe_col_indices: set[int],
    categories: list[str] | None = None,
) -> tuple[ColumnDataSource, list[TableColumn], int]:
    keys = [f"c{i}" for i in range(len(headers))]
    color_keys = {i: f"sharpe_color_{i}" for i in sharpe_col_indices}

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
            source_data[ck].append(_sharpe_color(row[col_idx]))
        source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
        display_row += 1

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    for col_idx, ck in color_keys.items():
        source_data[ck].append(_sharpe_color(total_row[col_idx]))
    source_data["row_style"].append(TOTAL_STYLE)

    source = ColumnDataSource(source_data)

    table_cols = []
    for i, h in enumerate(headers):
        if i in sharpe_col_indices:
            tmpl = (
                f'<div style="<%= row_style %>; color: <%= sharpe_color_{i} %>; '
                f'height: 100%; padding: 4px 10px; overflow: hidden; '
                f'text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">'
                f'<%= value %></div>'
            )
            fmt = HTMLTemplateFormatter(template=tmpl)
        else:
            fmt = HTMLTemplateFormatter(template=CELL_TEMPLATE)
        table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt))

    return source, table_cols, n_separators


class BokehSharpeTableRenderer(SharpeTableRenderer):
    def render(self, model: SharpeTableModel, output_path: str | None = None) -> None:
        subtitle = f"Risk-free rate: {model.risk_free_rate_pct:.2f}% (UK base rate)"

        # Main table: Fund Name, Ticker, Sharpe cols 2–7
        main_sharpe_cols = set(range(2, len(model.col_headers)))
        main_source, main_cols, main_seps = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row,
            sharpe_col_indices=main_sharpe_cols,
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

        # Category summary table
        cat_sharpe_cols = set(range(1, len(model.cat_col_headers)))
        cat_source, cat_cols, _ = _build_source_and_columns(
            model.cat_col_headers, model.cat_data_rows, model.cat_total_row,
            sharpe_col_indices=cat_sharpe_cols,
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
            make_title_div(f"Fund Portfolio \u2013 Sharpe Ratio  \u00b7  {subtitle}", 1000),
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
