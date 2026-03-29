"""
Fund Portfolio - Percentage Change Table
Shows percentage change in fund value over various time periods relative to current value.
"""

from fund_utils import CSV_PATH, load_funds, fetch_prices_gbp
from fund_table_renderer import TableModel, TableRenderer


def pct_change(current, past) -> str:
    """Format percentage change from past to current."""
    change = (current - past) / past * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%"


def build_rows(funds: list) -> tuple[list, list, list]:
    """Return (rows, totals, categories). totals = [total_now, total_prev, total_1w, total_1m, total_6m, total_1y]."""
    rows = []
    categories = []
    totals = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for f in funds:
        prices = fetch_prices_gbp(f["ticker"])
        price_now, price_prev, price_1w, price_1m, price_6m, price_1y = prices
        values = [p * f["units"] for p in prices]
        for i, v in enumerate(values):
            totals[i] += v
        rows.append([
            f["name"],
            f["ticker"],
            f"{f['units']:,}",
            pct_change(price_now, price_1y),
            pct_change(price_now, price_6m),
            pct_change(price_now, price_1m),
            pct_change(price_now, price_1w),
            pct_change(price_now, price_prev),
            f"£{values[0]:,.2f}",
        ])
        categories.append(f["category"])
    return rows, totals, categories


def build_table_model(funds: list) -> TableModel:
    """Build a TableModel from a list of fund dicts."""
    rows, totals, categories = build_rows(funds)
    total_now, total_prev, total_1w, total_1m, total_6m, total_1y = totals

    total_row = [
        "", "", "Total",
        pct_change(total_now, total_1y),
        pct_change(total_now, total_6m),
        pct_change(total_now, total_1m),
        pct_change(total_now, total_1w),
        pct_change(total_now, total_prev),
        f"£{total_now:,.2f}",
    ]

    col_headers = ["Fund Name", "Ticker", "Units", "1Y Change", "6M Change", "1M Change", "1W Change", "Prev Day", "Value"]

    return TableModel(
        col_headers=col_headers,
        rows=rows,
        total_row=total_row,
        categories=categories,
    )


def main(renderer: TableRenderer):
    print("Fetching fund data...")
    funds = load_funds(CSV_PATH)
    model = build_table_model(funds)
    renderer.render(model)


if __name__ == "__main__":
    from fund_table_matplotlib import MatplotlibTableRenderer
    main(MatplotlibTableRenderer())
