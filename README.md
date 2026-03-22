# Fund Tracker

A Python tool for displaying share/fund information fetched live from Yahoo Finance.

## Overview

This project retrieves up-to-date pricing data for investment funds and displays it in three ways:

- **fund_chart.py** — interactive price chart with selectable time periods (1M to 10Y)
- **fund_table.py** — portfolio table showing fund value at previous day, 1 week, 1 month, 6 months, 1 year, and current value, with a total row
- **fund_change_table.py** — portfolio table showing percentage change over the same time periods, with gains in green and losses in red

Funds are configured via a simple `funds.csv` file — no code changes needed to add or remove funds.

## Project Structure

| File | Description |
|------|-------------|
| `fund_chart.py` | Interactive price chart |
| `fund_table.py` | Absolute value table |
| `fund_change_table.py` | Percentage change table |
| `fund_utils.py` | Shared data loading and price fetching functions |
| `fund_constants.py` | Shared styling and layout constants |
| `funds.csv` | Your local fund configuration (not committed to git) |
| `funds.example.csv` | Example fund configuration for reference |

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

Display the absolute value table:

```bash
python fund_table.py
```

Display the percentage change table:

```bash
python fund_change_table.py
```

Display the interactive price chart:

```bash
python fund_chart.py
```

## Adding Funds

Copy `funds.example.csv` to `funds.csv` and add one row per fund. The file requires the following columns:

| Column | Description |
|--------|-------------|
| `name` | Display name of the fund |
| `ticker` | Yahoo Finance ticker symbol (UK funds typically use the format `0P0000XXXX.L`) |
| `units` | Number of units held |

`funds.csv` is excluded from version control so your personal fund data remains local.
