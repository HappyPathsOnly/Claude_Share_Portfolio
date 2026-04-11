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
_HERE = os.path.abspath(os.path.dirname(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from bokeh.models import ColumnDataSource, DataTable, TableColumn, HTMLTemplateFormatter
from bokeh.layouts import column
from bokeh.io import show

from renderers.fund_value_table_renderer import ValueTableModel, ValueTableRenderer
from bokeh_theme import (
    ROW_H, SEP_STYLE, CELL_TEMPLATE,
    TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
    make_table_stylesheet, table_height,
    page_css_div, make_title_div,
)


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

    n_separators = 0
    display_row = 0   # counts only real rows, so alternating colours ignore separators
    for i, row in enumerate(data_rows):
        # Insert a blank separator row when the category changes (skip before first row)
        if categories and i > 0 and categories[i] != categories[i - 1]:
            for k in keys:
                source_data[k].append("")
            source_data["row_style"].append(SEP_STYLE)
            n_separators += 1

        for k, v in zip(keys, row):
            source_data[k].append(v)
        source_data["row_style"].append(ODD_STYLE if display_row % 2 == 0 else EVEN_STYLE)
        display_row += 1

    for k, v in zip(keys, total_row):
        source_data[k].append(v)
    source_data["row_style"].append(TOTAL_STYLE)

    source = ColumnDataSource(source_data)

    table_cols = [
        TableColumn(field=k, title=h, formatter=HTMLTemplateFormatter(template=CELL_TEMPLATE))
        for k, h in zip(keys, headers)
    ]
    return source, table_cols, n_separators


class BokehValueTableRenderer(ValueTableRenderer):
    def render(self, model: ValueTableModel, output_path: str | None = None) -> None:
        # --- Main fund table ---
        main_source, main_cols, main_seps = _build_source_and_columns(
            model.col_headers, model.rows, model.total_row, categories=model.categories
        )
        main_table = DataTable(
            source=main_source,
            columns=main_cols,
            index_position=None,
            header_row=True,
            row_height=ROW_H,
            height=table_height(len(model.rows), main_seps),
            width=1380,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
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
            row_height=ROW_H,
            height=table_height(len(model.cat_data_rows)),
            width=870,
            sizing_mode="fixed",
            stylesheets=[make_table_stylesheet()],
        )

        layout = column(
            page_css_div(),
            make_title_div("Fund Portfolio", 1380),
            main_table,
            make_title_div("By Category", 870),
            cat_table,
        )
        if output_path:
            from bokeh.io import output_file, save
            output_file(output_path)
            save(layout)
        else:
            show(layout)
