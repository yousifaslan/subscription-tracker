# Yousif Aslan · 2309115995 · @yousifaslan

## My role
Developer and team lead: I built the main program and the command-line interface, and set up the GitHub repo.

## What I contributed
- **subscription_tracker.py**: the core logic:
  - Input checks used everywhere: `parse_name`, `parse_price`, `parse_cycle`, `parse_date` (reject bad values like `abc`, `-5`, `inf`, impossible dates)
  - Reading and saving the data file with `with open()`, skipping broken lines, and saving safely through a temporary file
  - Category dictionary with `.get(name, "Other")`
  - Monthly/yearly cost, `days_until`, `next_renewal` (December → January, short months)
  - Automation: `auto_renew()` moves past renewal dates forward automatically
  - Monthly budget feature and the statistics report (totals per category, most expensive, budget status)
  - Interactive menu with input validation loops
- **cli.py**: command-line interface with `argparse` sub-commands: `list`, `add`, `remove`, `upcoming`, `report`, `budget`, `menu`
- Tested the program with wrong and malicious input (bad prices, dates, names with commas/newlines, broken files) and fixed every crash
- Wrote the README, created the repo, organized the folders, invited the team, and fixed the README formatting
- I used Claude (an AI assistant) to help write and test the code; I reviewed every part and can explain how it works.

## Commits
- Subscription Tracker: CLI, interactive menu, budget and report
- Update README.md (fixed the example output formatting and a typo)

## What I learned
How to split a program into small functions, validate every input in one place, use dictionaries as lookup tables, read and write files safely, and build a real CLI with argparse.
