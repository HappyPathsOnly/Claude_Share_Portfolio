"""
Generates all three Bokeh HTML output files without opening a browser:
  fund_table.html          – current fund values
  fund_change_table.html   – percentage changes
  fund_chart.html          – price chart

Run directly or via the Playwright e2e global setup.
"""
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from fund_utils import CSV_PATH, load_funds
from fund_table import build_table_model as build_value_model
from fund_change_table import build_table_model as build_change_model
from fund_volatility_table import build_table_model as build_volatility_model
from fund_drawdown_table import build_table_model as build_drawdown_model
from fund_chart import build_chart_model
from GUI.Bokeh.fund_value_table_bokeh import BokehValueTableRenderer
from GUI.Bokeh.fund_change_table_bokeh import BokehChangeTableRenderer
from GUI.Bokeh.fund_volatility_table_bokeh import BokehVolatilityTableRenderer
from GUI.Bokeh.fund_drawdown_table_bokeh import BokehDrawdownTableRenderer
from GUI.Bokeh.fund_chart_bokeh import BokehChartRenderer


def generate_all() -> None:
    print("Loading fund data from CSV...")
    funds = load_funds(CSV_PATH)

    print("Generating fund_table.html...")
    BokehValueTableRenderer().render(
        build_value_model(funds),
        output_path=os.path.join(ROOT, "fund_table.html"),
    )

    print("Generating fund_change_table.html...")
    BokehChangeTableRenderer().render(
        build_change_model(funds),
        output_path=os.path.join(ROOT, "fund_change_table.html"),
    )

    print("Generating fund_volatility_table.html...")
    BokehVolatilityTableRenderer().render(
        build_volatility_model(funds),
        output_path=os.path.join(ROOT, "fund_volatility_table.html"),
    )

    print("Generating fund_drawdown_table.html...")
    BokehDrawdownTableRenderer().render(
        build_drawdown_model(funds),
        output_path=os.path.join(ROOT, "fund_drawdown_table.html"),
    )

    print("Generating fund_chart.html...")
    BokehChartRenderer().render(
        build_chart_model(),
        output_path=os.path.join(ROOT, "fund_chart.html"),
    )

    print("All HTML files generated.")


if __name__ == "__main__":
    generate_all()
