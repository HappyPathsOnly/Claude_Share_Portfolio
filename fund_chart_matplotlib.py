"""
Matplotlib renderer for the fund price chart.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.widgets import Button

from fund_chart_renderer import ChartModel, ChartRenderer


class MatplotlibChartRenderer(ChartRenderer):
    def render(self, model: ChartModel) -> None:
        print(f"  Latest price : {model.df['Price (p)'].iloc[-1]:,.2f}p  ({model.df.index[-1].date()})")

        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_axes([0.07, 0.18, 0.90, 0.72])
        self._draw(ax, model.df, model.period_label, model.fund_name)

        # --- Period buttons ---
        period_labels = model.period_labels
        n = len(period_labels)
        btn_width = 0.09
        btn_height = 0.06
        gap = 0.01
        total_width = n * btn_width + (n - 1) * gap
        x_start = (1.0 - total_width) / 2

        buttons = []
        active_label = [model.period_label]

        def make_callback(label):
            def on_click(_event):
                if label == active_label[0]:
                    return
                active_label[0] = label
                print(f"  Loading {label}...")
                new_df = model.fetch_fn(label)
                self._draw(ax, new_df, label, model.fund_name)
                for btn, lbl in zip(buttons, period_labels):
                    btn.color = "#0057a8" if lbl == label else "#e0e8f5"
                    btn.hovercolor = "#003d7a" if lbl == label else "#c5d5ea"
                    btn.label.set_color("white" if lbl == label else "#0057a8")
                fig.canvas.draw_idle()
            return on_click

        for i, label in enumerate(period_labels):
            x = x_start + i * (btn_width + gap)
            btn_ax = fig.add_axes([x, 0.04, btn_width, btn_height])
            is_active = label == model.period_label
            btn = Button(
                btn_ax, label,
                color="#0057a8" if is_active else "#e0e8f5",
                hovercolor="#003d7a" if is_active else "#c5d5ea",
            )
            btn.label.set_color("white" if is_active else "#0057a8")
            btn.label.set_fontsize(10)
            btn.on_clicked(make_callback(label))
            buttons.append(btn)

        plt.show()

    def _draw(self, ax, df, period_label: str, fund_name: str):
        """Redraw the chart on the given axes."""
        ax.clear()
        ax.plot(df.index, df["Price (p)"], linewidth=1.8, color="#0057a8")
        ax.fill_between(df.index, df["Price (p)"], alpha=0.10, color="#0057a8")

        latest_price = df["Price (p)"].iloc[-1]
        start_price = df["Price (p)"].iloc[0]
        change_pct = (latest_price - start_price) / start_price * 100
        sign = "+" if change_pct >= 0 else ""

        ax.set_title(
            f"{fund_name}  |  {period_label} return: {sign}{change_pct:.2f}%",
            fontsize=13, pad=10,
        )
        ax.set_ylabel("Price (pence)", fontsize=11)
        ax.set_xlabel("")

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.figure.autofmt_xdate(rotation=30, ha="right")

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}p"))
        price_min = df["Price (p)"].min()
        price_max = df["Price (p)"].max()
        margin = (price_max - price_min) * 0.05
        ax.set_ylim(price_min - margin, price_max + margin)

        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)

        ax.annotate(
            f"  {latest_price:,.2f}p",
            xy=(df.index[-1], latest_price),
            fontsize=10, color="#0057a8", va="center",
        )

        ax.figure.canvas.draw_idle()
