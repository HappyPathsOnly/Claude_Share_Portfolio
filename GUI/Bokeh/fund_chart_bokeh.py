"""
Bokeh renderer for the fund price chart.
Opens an interactive chart in a browser tab.

All period data is pre-fetched at startup and embedded in the page, so
period switching happens instantly in the browser without a Python server.
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
        ColumnDataSource, CustomJS, RadioButtonGroup, Div, Label,
        HoverTool, CustomJSTickFormatter, DatetimeTickFormatter, Range1d,
    )
    from bokeh.plotting import figure
    from bokeh.layouts import column
    from bokeh.io import show
except ImportError as exc:
    raise ImportError(
        "Missing dependency: bokeh is required to run fund_chart_bokeh. "
        "Install it with: pip install bokeh"
    ) from exc

from fund_chart_renderer import ChartModel, ChartRenderer
from fund_constants import HEADER_BG

# Palette
_BLUE       = HEADER_BG          # "#0057a8"
_BTN_ACTIVE = "#0057a8"
_BTN_IDLE   = "#e0e8f5"


def _to_ms(index) -> list[int]:
    """Convert a pandas DatetimeIndex to JavaScript timestamps (ms since epoch)."""
    return [int(ts.timestamp() * 1000) for ts in index]


def _y_bounds(ys: list[float]) -> tuple[float, float]:
    margin = (max(ys) - min(ys)) * 0.05
    return min(ys) - margin, max(ys) + margin


def _title_html(fund_name: str, label: str, ys: list[float]) -> str:
    change = (ys[-1] - ys[0]) / ys[0] * 100
    sign = "+" if change >= 0 else ""
    return (
        f'<h3 style="color:{_BLUE}; font-family:sans-serif; margin:4px 0 2px 0;">'
        f"{fund_name}&nbsp;&nbsp;|&nbsp;&nbsp;{label} return: {sign}{change:.2f}%</h3>"
    )


class BokehChartRenderer(ChartRenderer):
    def render(self, model: ChartModel) -> None:
        # --- Pre-fetch all periods ---
        print("  Pre-fetching all periods for Bokeh chart...")
        all_data: dict[str, dict] = {}
        for label in model.period_labels:
            print(f"    {label}...", end=" ", flush=True)
            df = model.fetch_fn(label)
            xs = _to_ms(df.index)
            ys = df["Price (p)"].tolist()
            all_data[label] = {"x": xs, "y": ys, "y_base": [0.0] * len(xs)}
            print("done")

        # --- Initial period ---
        init_label = model.period_label
        init = all_data[init_label]
        y_start, y_end = _y_bounds(init["y"])

        source = ColumnDataSource(data=dict(
            x=init["x"],
            y=init["y"],
            y_base=init["y_base"],
        ))

        # --- Title ---
        title_div = Div(text=_title_html(model.fund_name, init_label, init["y"]))

        # --- Figure ---
        p = figure(
            x_axis_type="datetime",
            y_range=Range1d(y_start, y_end),
            x_range=Range1d(init["x"][0], init["x"][-1]),
            height=450,
            width=1100,
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )
        p.toolbar.logo = None
        p.outline_line_color = None
        p.grid.grid_line_alpha = 0.35
        p.grid.grid_line_dash = [4, 4]
        p.xgrid.grid_line_color = None

        p.line("x", "y", source=source, line_width=2, color=_BLUE)
        p.varea("x", "y_base", "y", source=source, fill_alpha=0.10, fill_color=_BLUE)

        # Latest-price annotation
        price_label = Label(
            x=init["x"][-1],
            y=init["y"][-1],
            text=f"  {init['y'][-1]:,.2f}p",
            text_color=_BLUE,
            text_font_size="10px",
            x_units="data",
            y_units="data",
        )
        p.add_layout(price_label)

        # Axis formatting
        p.xaxis.formatter = DatetimeTickFormatter(months="%b '%y", years="%Y")
        p.yaxis.formatter = CustomJSTickFormatter(
            code="return Math.round(tick).toLocaleString() + 'p';"
        )
        p.yaxis.axis_label = "Price (pence)"
        p.yaxis.axis_label_text_font_size = "11px"

        # Hover tool
        hover = HoverTool(
            tooltips=[
                ("Date",  "@x{%d %b %Y}"),
                ("Price", "@y{0,0.00}p"),
            ],
            formatters={"@x": "datetime"},
            mode="vline",
        )
        p.add_tools(hover)

        # --- Period RadioButtonGroup ---
        btn_group = RadioButtonGroup(
            labels=model.period_labels,
            active=model.period_labels.index(init_label),
            width=400,
        )

        # CSS to style the active/inactive buttons to match the project palette
        btn_css = Div(text=f"""
<style>
  .bk-btn-group button.bk-btn {{
    background-color: {_BTN_IDLE};
    color: {_BLUE};
    border-color: {_BLUE};
    font-weight: bold;
    font-family: sans-serif;
  }}
  .bk-btn-group button.bk-btn.bk-active {{
    background-color: {_BTN_ACTIVE};
    color: white;
  }}
</style>
""")

        # --- JavaScript callback: switch period ---
        callback = CustomJS(
            args=dict(
                source=source,
                all_data=all_data,
                labels=model.period_labels,
                title_div=title_div,
                fund_name=model.fund_name,
                y_range=p.y_range,
                x_range=p.x_range,
                price_label=price_label,
            ),
            code="""
const label = labels[cb_obj.active];
const d = all_data[label];

source.data = {x: d.x, y: d.y, y_base: d.y_base};

// Update axis ranges
const ys = d.y;
const ymin = Math.min(...ys);
const ymax = Math.max(...ys);
const margin = (ymax - ymin) * 0.05;
y_range.start = ymin - margin;
y_range.end   = ymax + margin;
x_range.start = d.x[0];
x_range.end   = d.x[d.x.length - 1];

// Update title with new return %
const change = (ys[ys.length - 1] - ys[0]) / ys[0] * 100;
const sign = change >= 0 ? '+' : '';
title_div.text =
    '<h3 style="color:' + '""" + _BLUE + """' + '; font-family:sans-serif; margin:4px 0 2px 0;">'
    + fund_name + '&nbsp;&nbsp;|&nbsp;&nbsp;' + label
    + ' return: ' + sign + change.toFixed(2) + '%</h3>';

// Update latest-price annotation
const last_y = ys[ys.length - 1];
price_label.x    = d.x[d.x.length - 1];
price_label.y    = last_y;
price_label.text = '  ' + last_y.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + 'p';

source.change.emit();
""",
        )
        btn_group.js_on_change("active", callback)

        show(column(btn_css, title_div, p, btn_group))
