# Subscription Tracker

**COE203 Advanced Programming with Python · Project 1 · Group Pypeople**

A command-line tool that keeps track of all your subscriptions (Netflix, Spotify, gym, cloud storage…),
warns you before a payment is taken, and shows how much you really spend every month and every year.

## The problem it solves
Subscriptions are small, automatic and easy to forget. Most people can't say how much they pay per month in total,
when the next charge comes, or which service costs the most. Banks show payments **after** they happen.
This tool shows them **before**: upcoming renewals, totals per category, and a warning when you go over your own monthly budget.

## Features
- **Category dictionary:** every subscription is put in a category (Entertainment, Music, Productivity…). Unknown services go to *Other*.
- **Monthly and yearly cost:** yearly plans are converted to a monthly cost, so everything can be compared and added up.
- **Upcoming renewals:** shows what will be charged in the next N days, soonest first, with a *SOON!* warning at 3 days or less.
- **Automation (auto-renew):** when a renewal date has passed, the program moves it to the next billing date by itself and saves the file.
- **Monthly budget:** set a limit and the report shows how much is used, how much is left, or how much you are over.
- **Statistics report:** count, monthly and yearly totals, most expensive subscription, budget status, and spending per category with percentages. It can be saved to a file.
- **Two ways to use it:** a command-line interface with arguments (`cli.py`) and an interactive menu.
- **Input validation:** every value (from the command line, the menu, or the data file) is checked in one place, so bad or malicious input is rejected with a clear message instead of crashing the program.

## Project structure
```
subscription-tracker/
├── cli.py                      # Command-line interface: one command per feature, with arguments (argparse)
├── subscription_tracker.py     # Core logic: input checks, file reading/saving, auto-renew, budget, report, interactive menu
├── data/
│   ├── subscriptions.txt       # Your subscriptions (read and updated by the program)
│   └── sample_subscriptions.txt# Clean example data, used to reset subscriptions.txt
├── contributions/              # One file per team member describing their contribution
├── README.md                   # This file
└── .gitignore                  # Keeps generated files (report, budget, caches) out of the repo
```
Files created while running (not in the repo): `data/report.txt` (saved report) and `data/budget.txt` (your monthly budget).

## Requirements
Python 3.8 or newer. Only the standard library is used (`argparse`, `datetime`, `calendar`, `math`, `os`, `sys`), so there is nothing to install.

## Usage: command line (`cli.py`)
```bash
python3 cli.py --help                 # list all commands
python3 cli.py <command> --help       # help for one command
```

| Command | What it does | Example |
|---|---|---|
| `list` | Table of all subscriptions. `--sort date\|price\|name`, `--category NAME` | `python3 cli.py list --sort price` |
| `add` | Add a subscription (all four arguments are required) | `python3 cli.py add --name Netflix --price 229.99 --cycle monthly --renewal 2026-10-20` |
| `remove` | Remove a subscription by name (capital letters don't matter) | `python3 cli.py remove --name netflix` |
| `upcoming` | Renewals in the next N days (0–365, default 7) | `python3 cli.py upcoming --days 14` |
| `report` | Full spending report; `--save` also writes `data/report.txt` | `python3 cli.py report --save` |
| `budget` | Show the budget, set it, or remove it with `--clear` | `python3 cli.py budget 3000` |
| `menu` | Open the interactive menu | `python3 cli.py menu` |

Every command first loads `data/subscriptions.txt` and runs auto-renew.
Errors are printed to *stderr* and the program exits with code 1 (or 2 for invalid arguments), so it can also be used from scripts.

> On Windows, use `python` instead of `python3`.

## Usage: interactive menu
```bash
python3 subscription_tracker.py
```
```
========= SUBSCRIPTION TRACKER =========
1) Show all    2) Upcoming    3) Add
4) Remove      5) Report      6) Budget    0) Exit
```
When adding, every question is asked again until the answer is valid. Ctrl+C or Ctrl+D exits cleanly.

## Data file format (`data/subscriptions.txt`)
One subscription per line: `name,price,cycle,next_renewal`
```
Netflix,229.99,monthly,2026-10-12
Adobe,4500.0,yearly,2027-02-01
```
Lines starting with `#` are comments. Invalid lines are skipped with a message that shows the line number.
To start over with the example data:
```bash
cp data/sample_subscriptions.txt data/subscriptions.txt
```

## Input rules
| Value | Rule |
|---|---|
| Name | 1–40 printable characters, no commas, cannot start with `#`, must be unique (capital letters ignored) |
| Price / budget | A normal number greater than 0 and at most 1,000,000 (rejects `abc`, `-5`, `inf`, `nan`), rounded to 2 decimals |
| Cycle | `monthly` or `yearly` (`m` and `y` also work) |
| Renewal date | A real date `YYYY-MM-DD` between 2000 and 2100 |
| Days | A whole number from 0 to 365 |

The data file is saved through a temporary file that then replaces the real one, so it is never left half-written.
Unreadable files, missing files and permission problems are reported with a message instead of a crash.

## How it works
1. **Load:** `load_subscriptions()` reads the file line by line, splits each line at the commas and checks every value with `parse_name`, `parse_price`, `parse_cycle` and `parse_date`.
2. **Categorize:** `get_category()` looks the name up in the `CATEGORIES` dictionary with `.get(name, "Other")`.
3. **Auto-renew:** `auto_renew()` uses a `while` loop to move each past date forward with `next_renewal()`. That function handles December → January and short months (Jan 31 → Feb 28).
4. **Report:** `build_report()` adds up the monthly cost of every subscription (accumulator pattern), totals per category in a dictionary, and finds the most expensive one. `format_report()` turns it into text with f-strings.
5. **CLI:** `cli.py` builds an `argparse` parser with one sub-command per feature. Argument types reuse the same `parse_*` functions, so the command line and the menu follow exactly the same rules.

## Team
See the `contributions/` folder.
