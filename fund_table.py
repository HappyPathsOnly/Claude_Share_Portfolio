"""
Fund Portfolio - Value Table
Displays current fund values in a tabular format.
"""

from collections import defaultdict
from utils.fund_utils import CSV_PATH, load_funds, fetch_prices_gbp
from renderers.fund_value_table_renderer import ValueTableModel, ValueTableRenderer


def build_rows(funds: list) -> tuple:
    """Return (rows, total_now, total_prev, total_1w, total_1m, total_6m, total_1y, category_totals, categories)."""
    rows = []
    categories = []
    totals = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    category_totals = defaultdict(lambda: [0.0] * 6)
    for f in funds:
        prices = fetch_prices_gbp(f["ticker"])
        values = [p * f["units"] for p in prices]
        for i, v in enumerate(values):
            totals[i] += v
            category_totals[f["category"]][i] += v
        rows.append([
            f["name"],
            f["ticker"],
            f"{f['units']:,}",
            f"£{values[5]:,.2f}",
            f"£{values[4]:,.2f}",
            f"£{values[3]:,.2f}",
            f"£{values[2]:,.2f}",
            f"£{values[1]:,.2f}",
            f"£{values[0]:,.2f}",
        ])
        categories.append(f["category"])
    return rows, *totals, dict(category_totals), categories


def build_table_model(funds: list) -> ValueTableModel:
    """Build a ValueTableModel from a list of fund dicts."""
    rows, total_now, total_prev, total_1w, total_1m, total_6m, total_1y, category_totals, categories = build_rows(funds)

    col_headers = ["Fund Name", "Ticker", "Units", "Value (1Y ago)", "Value (6M ago)", "Value (1M ago)", "Value (1W ago)", "Prev Day", "Value"]

    total_row = [
        "", "", "Total",
        f"£{total_1y:,.2f}", f"£{total_6m:,.2f}", f"£{total_1m:,.2f}", f"£{total_1w:,.2f}",
        f"£{total_prev:,.2f}", f"£{total_now:,.2f}",
    ]

    cat_col_headers = ["Category", "Value (1Y ago)", "Value (6M ago)", "Value (1M ago)", "Value (1W ago)", "Prev Day", "Value"]

    cat_total = [0.0] * 6
    cat_data_rows = []
    for cat in sorted(category_totals):
        v = category_totals[cat]
        for i in range(6):
            cat_total[i] += v[i]
        cat_data_rows.append([
            cat,
            f"£{v[5]:,.2f}", f"£{v[4]:,.2f}", f"£{v[3]:,.2f}",
            f"£{v[2]:,.2f}", f"£{v[1]:,.2f}", f"£{v[0]:,.2f}",
        ])

    cat_total_row = [
        "Total",
        f"£{cat_total[5]:,.2f}", f"£{cat_total[4]:,.2f}", f"£{cat_total[3]:,.2f}",
        f"£{cat_total[2]:,.2f}", f"£{cat_total[1]:,.2f}", f"£{cat_total[0]:,.2f}",
    ]

    return ValueTableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=total_row,
        categories=categories,
        cat_col_headers=cat_col_headers,
        cat_data_rows=cat_data_rows,
        cat_total_row=cat_total_row,
    )


def main(renderer: ValueTableRenderer):
    print("Fetching fund data...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fund value table")
    parser.add_argument("--matplotlib", action="store_true", help="Use Matplotlib renderer (opens a window)")
    args = parser.parse_args()

    if args.matplotlib:
        from GUI.Matplotlib.fund_value_table_matplotlib import MatplotlibValueTableRenderer
        main(MatplotlibValueTableRenderer())
    else:
        from GUI.Bokeh.fund_value_table_bokeh import BokehValueTableRenderer
        main(BokehValueTableRenderer())
