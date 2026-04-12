"""
Bokeh renderer for the fund inter-fund correlation matrix.

Correlation cells are heat-mapped by diversification quality:
  - Diagonal (self-correlation = 1.00): grey
  - >= 0.80 (highly correlated, poor diversification): red
  - 0.50–0.80 (moderate correlation): amber
  - < 0.50 (low correlation, good diversification): green
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

from renderers.fund_correlation_table_renderer import CorrelationTableModel, CorrelationTableRenderer
from utils.fund_constants import ROW_FG, GREEN, RED
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)

_AMBER      = "#c97a00"
_DIAG_COLOR = "#888888"   # Self-correlation diagonal — always 1.00, neutral grey

_NAME_COL_W = 200   # px for the fund name column
_CORR_COL_W = 80    # px per correlation column


def _corr_color(text: str, is_diagonal: bool) -> str:
    """Return a heat-map CSS colour for a correlation value string like '0.85'."""
    if is_diagonal:
        return _DIAG_COLOR
    try:
        val = float(text)
    except ValueError:
        return ROW_FG
    if val >= 0.80:
        return RED
    if val >= 0.50:
        return _AMBER
    return GREEN


def _build_source_and_columns(
    headers: list[str],
    data_rows: list[list[str]],
    categories: list[str],
    n_funds: int,
) -> tuple[ColumnDataSource, list[TableColumn], int]:
    """
    Build a ColumnDataSource and TableColumn list for the correlation matrix.

    Column 0 is the fund name (plain text).
    Columns 1..N are the correlation values, each with its own per-cell colour key
    so the diagonal can be styled differently from off-diagonal cells.
    """
    keys = [f"c{i}" for i in range(len(headers))]
    # One colour key per correlation column
    corr_col_indices = list(range(1, n_funds + 1))
    color_keys = {i: f"corr_color_{i}" for i in corr_col_indices}

    source_data: dict[str, list] = {k: [] for k in keys}
    for ck in color_keys.values():
        source_data[ck] = []
    source_data["row_style"] = []

    n_separators = 0
    display_row = 0
    fund_row_idx = 0   # tracks which fund row we're on (ignoring separators)

    for i, row in enumerate(data_rows):
        # Insert a blank separator row between different categories
        if i > 0 and categories[i] != categories[i - 1]:
            for k in keys:
                source_data[k].append("")
            for ck in color_keys.values():
                source_data[ck].append(ROW_FG)
            source_data["row_style"].append(SEP_STYLE)
            n_separators += 1

        for k, v in zip(keys, row):
            source_data[k].append(v)

        for col_idx, ck in color_keys.items():
            is_diag = (col_idx - 1 == fund_row_idx)
            source_data[ck].append(_corr_color(row[col_idx], is_diag))

        source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
        display_row += 1
        fund_row_idx += 1

    source = ColumnDataSource(source_data)

    table_cols = []
    for i, h in enumerate(headers):
        if i in color_keys:
            tmpl = (
                f'<div style="<%= row_style %>; color: <%= corr_color_{i} %>; '
                f'height: 100%; padding: 4px 10px; overflow: hidden; '
                f'text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box; '
                f'font-weight: <%= corr_color_{i} === "{_DIAG_COLOR}" ? "400" : "700" %>;">'
                f'<%= value %></div>'
            )
            fmt = HTMLTemplateFormatter(template=tmpl)
            table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt, width=_CORR_COL_W))
        else:
            fmt = HTMLTemplateFormatter(template=CELL_TEMPLATE)
            table_cols.append(TableColumn(field=keys[i], title=h, formatter=fmt, width=_NAME_COL_W))

    return source, table_cols, n_separators


_LEGEND = [
    (_DIAG_COLOR, "1.00",        "Self-correlation (diagonal)"),
    (RED,         "≥ 0.80",      "Highly correlated — poor diversification"),
    (_AMBER,      "0.50 – 0.79", "Moderate correlation"),
    (GREEN,       "< 0.50",      "Low correlation — good diversification"),
]

_SECTION_LABEL = (
    'font-weight:700; margin-bottom:6px; color:#0057a8; '
    'text-transform:uppercase; letter-spacing:0.06em; font-size:11px;'
)


def _make_key_div(abbrev_key: list[tuple[str, str]], width: int) -> "Div":
    """Return a styled Div with the abbreviation key and colour legend side by side."""
    abbrev_rows = "".join(
        f'<tr>'
        f'<td style="padding:2px 20px 2px 0; font-family:monospace; font-weight:700; '
        f'white-space:nowrap; color:#0057a8;">{ab}</td>'
        f'<td style="padding:2px 0; color:#333;">{name}</td>'
        f'</tr>'
        for ab, name in abbrev_key
    )
    abbrev_html = (
        f'<div style="margin-right:40px;">'
        f'<div style="{_SECTION_LABEL}">Abbreviation Key</div>'
        f'<table style="border-collapse:collapse;">{abbrev_rows}</table>'
        f'</div>'
    )

    legend_rows = "".join(
        f'<tr>'
        f'<td style="padding:2px 12px 2px 0; white-space:nowrap;">'
        f'<span style="display:inline-block; width:10px; height:10px; border-radius:2px; '
        f'background:{color}; margin-right:6px; vertical-align:middle;"></span>'
        f'<span style="font-weight:700; color:{color}; font-family:monospace;">{label}</span>'
        f'</td>'
        f'<td style="padding:2px 0; color:#333;">{desc}</td>'
        f'</tr>'
        for color, label, desc in _LEGEND
    )
    legend_html = (
        f'<div>'
        f'<div style="{_SECTION_LABEL}">Colour Key</div>'
        f'<table style="border-collapse:collapse;">{legend_rows}</table>'
        f'</div>'
    )

    html = (
        f'<div style="width:{width}px; background:#fff; border:1px solid #b0c4de; '
        f'border-top:none; padding:10px 16px 12px; '
        f'font-family:\'Segoe UI\',Arial,sans-serif; font-size:12px;">'
        f'<div style="display:flex; align-items:flex-start;">'
        f'{abbrev_html}{legend_html}'
        f'</div>'
        f'</div>'
    )
    from bokeh.models import Div
    return Div(text=html)


class BokehCorrelationTableRenderer(CorrelationTableRenderer):
    def render(self, model: CorrelationTableModel, output_path: str | None = None) -> None:
        source, cols, n_seps = _build_source_and_columns(
            model.col_headers,
            model.rows,
            model.categories,
            model.n_funds,
        )

        table_width = _NAME_COL_W + model.n_funds * _CORR_COL_W

        table = DataTable(
            source=source,
            columns=cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.rows), n_seps),
            width=table_width,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        title_text = f"Fund Portfolio \u2013 Correlation Matrix ({model.period})"
        layout = column(
            page_css_div(),
            make_title_div(title_text, table_width),
            table,
            _make_key_div(model.abbrev_key, table_width),
        )

        if output_path:
            from bokeh.io import output_file, save
            output_file(output_path)
            save(layout)
        else:
            show(layout)
