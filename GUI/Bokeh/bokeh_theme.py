"""
Shared Bokeh theme: CSS strings, constants, and helper functions reused across all pages.

Import what you need, e.g.:
    from bokeh_theme import (
        BLUE, DARK_BLUE,
        TABLE_CSS, BTN_CSS,
        ROW_H, SEP_STYLE, CELL_TEMPLATE,
        TOTAL_STYLE, ODD_STYLE, EVEN_STYLE,
        make_table_stylesheet, table_height,
        page_css_div, make_title_div,
    )
"""

import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bokeh.models import Div, InlineStyleSheet

from fund_constants import HEADER_BG, TOTAL_BG, TOTAL_FG, ROW_BG_ODD, ROW_BG_EVEN, ROW_FG

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BLUE      = HEADER_BG   # "#0057a8"
DARK_BLUE = "#003d7a"

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
ROW_H    = 30   # px per data row
HEADER_H = 32   # px for the header row

# ---------------------------------------------------------------------------
# Row styles (inline CSS applied per-row via ColumnDataSource)
# ---------------------------------------------------------------------------
TOTAL_STYLE = f"font-weight: 700; background-color: {TOTAL_BG}; color: {TOTAL_FG}; font-size: 13px;"
ODD_STYLE   = f"background-color: {ROW_BG_ODD};  color: {ROW_FG};"
EVEN_STYLE  = f"background-color: {ROW_BG_EVEN}; color: {ROW_FG};"

# Blank separator row — matches the page background so it reads as a visual gap.
SEP_STYLE = "background-color: #f0f4f8; pointer-events: none;"

# ---------------------------------------------------------------------------
# Cell template (base — no per-cell colour override)
# ---------------------------------------------------------------------------
CELL_TEMPLATE = """
<div style="<%= row_style %>; height: 100%; padding: 4px 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; box-sizing: border-box;">
  <%= value %>
</div>
"""

# ---------------------------------------------------------------------------
# Shadow-DOM CSS for DataTable widgets
# ---------------------------------------------------------------------------
TABLE_CSS = f"""
  .slick-header-columns {{
    background: {BLUE} !important;
  }}
  .slick-header-column {{
    background: linear-gradient(180deg, {BLUE} 0%, {DARK_BLUE} 100%) !important;
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

# ---------------------------------------------------------------------------
# Shadow-DOM CSS for RadioButtonGroup widgets
# ---------------------------------------------------------------------------
BTN_CSS = f"""
  :host {{
    font-family: 'Segoe UI', Arial, sans-serif;
  }}
  .bk-btn {{
    background-color: #e0e8f5 !important;
    color: {BLUE} !important;
    border-color: {BLUE} !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 0.04em !important;
  }}
  .bk-btn.bk-active {{
    background: linear-gradient(180deg, {BLUE} 0%, {DARK_BLUE} 100%) !important;
    color: white !important;
  }}
  .bk-btn:hover:not(.bk-active) {{
    background-color: #c8d8ee !important;
  }}
"""

# ---------------------------------------------------------------------------
# Light-DOM page CSS (body background / font)
# ---------------------------------------------------------------------------
_PAGE_CSS_HTML = """
<style>
  body {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 16px;
  }
</style>
"""


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def page_css_div() -> Div:
    """Return a Div that injects body-level page styles."""
    return Div(text=_PAGE_CSS_HTML)


def make_table_stylesheet() -> InlineStyleSheet:
    """Return a fresh InlineStyleSheet for a DataTable (each widget needs its own instance)."""
    return InlineStyleSheet(css=TABLE_CSS)


def table_height(n_data_rows: int, n_separators: int = 0) -> int:
    """Height in px to show all rows without a scrollbar."""
    return HEADER_H + (n_data_rows + 1 + n_separators) * ROW_H + 8


def make_title_div(text: str, width: int) -> Div:
    """Return a Div with a gradient header bar containing centred uppercase text."""
    html = (
        f'<div style="width:{width}px;">'
        f'<div style="background:linear-gradient(180deg,{BLUE} 0%,{DARK_BLUE} 100%); '
        f'padding:10px 16px; border-radius:4px 4px 0 0; text-align:center;">'
        f'<span style="color:white; font-family:\'Segoe UI\',Arial,sans-serif; '
        f'font-size:14px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">'
        f'{text}</span></div></div>'
    )
    return Div(text=html)
