# Fund Tracker

A Python tool for displaying share/fund information fetched live from Yahoo Finance.

## Overview

This project retrieves up-to-date pricing data for investment funds and displays it in two ways:

- **fund_chart.py** — interactive price chart with selectable time periods (1M to 10Y)
- **fund_table.py** — portfolio table showing fund name, ticker, units held, and current value, with a total row

Funds are configured via a simple `funds.csv` file — no code changes needed to add or remove funds.

## Built With

- **Python**
- **[yfinance](https://github.com/ranaroussi/yfinance)** — fetches live pricing data from Yahoo Finance
- **[matplotlib](https://matplotlib.org/)** — renders charts and tables
- **[Claude](https://claude.ai/)** — AI assistant used to develop this project

## Getting Started

### Prerequisites

Python 3.10+ is recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running

Display the portfolio table:

```bash
python fund_table.py
```

Display the price chart for the Fidelity Index World Fund:

```bash
python fund_chart.py
```

## Adding Funds

Edit `funds.csv` and add one row per fund. The file requires the following columns:

| Column | Description |
|--------|-------------|
| `name` | Display name of the fund |
| `ticker` | Yahoo Finance ticker symbol (UK funds typically use the format `0P0000XXXX.L`) |
| `units` | Number of units held |
