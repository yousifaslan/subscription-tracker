"""
Subscription Tracker - COE203 Project 1

Core logic for tracking subscriptions: reading and saving the data file,
checking every input, renewing old dates automatically, budget tracking
and the spending report. Running this file directly opens the interactive menu.

Usage:
    python3 subscription_tracker.py      # interactive menu
    python3 cli.py --help                # command-line interface with arguments
"""

import calendar
import math
import os
from datetime import date

# ---------- Constants ----------
FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(FOLDER, "data")
DATA_FILE = os.path.join(DATA_FOLDER, "subscriptions.txt")
BUDGET_FILE = os.path.join(DATA_FOLDER, "budget.txt")
REPORT_FILE = os.path.join(DATA_FOLDER, "report.txt")

CURRENCY = "TL"
WARNING_DAYS = 3
CYCLES = ("monthly", "yearly")
MAX_NAME_LENGTH = 40
MAX_PRICE = 1_000_000
FIRST_YEAR = 2000
LAST_YEAR = 2100

CATEGORIES = {
    "netflix": "Entertainment",
    "youtube premium": "Entertainment",
    "amazon prime": "Entertainment",
    "disney+": "Entertainment",
    "spotify": "Music",
    "apple music": "Music",
    "icloud": "Cloud Storage",
    "google one": "Cloud Storage",
    "chatgpt plus": "Productivity",
    "adobe": "Productivity",
    "microsoft 365": "Productivity",
    "duolingo": "Education",
    "gym": "Health",
    "youtube music": "Music",
    "canva": "Productivity",
    "notion": "Productivity",
    "xbox game pass": "Gaming",
    "playstation plus": "Gaming",
}


# ---------- Checking input (every value goes through these) ----------
def parse_name(text):
    """Return a clean subscription name, or raise ValueError explaining the problem."""
    name = str(text).strip()
    if name == "":
        raise ValueError("Name cannot be empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Name is too long (max {MAX_NAME_LENGTH} characters).")
    if "," in name or name.startswith("#") or not name.isprintable():
        raise ValueError("Name cannot contain commas, start with #, or contain special characters.")
    return name


def parse_price(text):
    """Return a safe positive price, or raise ValueError explaining the problem."""
    try:
        price = float(str(text).strip())
    except ValueError:
        raise ValueError("Price must be a number, for example 99.90") from None
    if not math.isfinite(price):
        raise ValueError("Price must be a normal number.")
    price = round(price, 2)
    if price <= 0:
        raise ValueError("Price must be more than 0.")
    if price > MAX_PRICE:
        raise ValueError(f"Price is too high (max {MAX_PRICE:,}).")
    return price


def parse_cycle(text):
    """Return 'monthly' or 'yearly' (m and y also work), or raise ValueError."""
    cycle = str(text).strip().lower()
    if cycle in ("monthly", "m"):
        return "monthly"
    if cycle in ("yearly", "y"):
        return "yearly"
    raise ValueError("Cycle must be monthly or yearly.")


def parse_date(text):
    """Return a date from YYYY-MM-DD text, or raise ValueError."""
    try:
        renewal = date.fromisoformat(str(text).strip())
    except ValueError:
        raise ValueError("Date must be a real date like 2026-11-01") from None
    if not FIRST_YEAR <= renewal.year <= LAST_YEAR:
        raise ValueError(f"Date must be between {FIRST_YEAR} and {LAST_YEAR}.")
    return renewal


# ---------- Subscriptions ----------
def get_category(name):
    """Return the category of a subscription, or 'Other' if we don't know it."""
    return CATEGORIES.get(name.strip().lower(), "Other")


def make_subscription(name, price, cycle, renewal):
    """Build one subscription record (a dictionary)."""
    return {
        "name": name,
        "price": price,
        "cycle": cycle,
        "renewal": renewal,
        "category": get_category(name),
    }


def find_subscription(subscriptions, name):
    """Return the subscription with this name (ignoring capital letters), or None."""
    for sub in subscriptions:
        if sub["name"].lower() == name.strip().lower():
            return sub
    return None


def add_subscription(subscriptions, name, price, cycle, renewal):
    """Check the values and add a new subscription. Returns an error message, or '' if it worked."""
    try:
        new_sub = make_subscription(parse_name(name), parse_price(price),
                                    parse_cycle(cycle), parse_date(renewal))
    except ValueError as error:
        return str(error)
    if find_subscription(subscriptions, new_sub["name"]) is not None:
        return f"{new_sub['name']} is already in your list."
    subscriptions.append(new_sub)
    return ""


def remove_subscription(subscriptions, name):
    """Remove a subscription by name. Returns the removed one, or None if not found."""
    sub = find_subscription(subscriptions, name)
    if sub is not None:
        subscriptions.remove(sub)
    return sub


# ---------- Files ----------
def load_subscriptions(filename):
    """Read the data file and return a list of subscriptions. Bad lines are skipped."""
    subscriptions = []
    try:
        with open(filename, encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) != 4:
                    print(f"Skipping line {line_number}: expected 4 values, found {len(parts)}.")
                    continue
                error = add_subscription(subscriptions, *parts)
                if error:
                    print(f"Skipping line {line_number}: {error}")
    except FileNotFoundError:
        print("No data file yet - starting with an empty list.")
    except UnicodeDecodeError:
        print(f"{os.path.basename(filename)} is not a readable text file - starting with an empty list.")
    except OSError as error:
        print(f"Could not read {os.path.basename(filename)}: {error}")
    return subscriptions


def save_subscriptions(filename, subscriptions):
    """Write all subscriptions to the data file safely. Returns True if it worked."""
    temp_file = filename + ".tmp"
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(temp_file, "w", encoding="utf-8") as file:
            file.write("# name,price,cycle,next_renewal (YYYY-MM-DD)\n")
            for sub in subscriptions:
                file.write(f"{sub['name']},{sub['price']},{sub['cycle']},{sub['renewal']}\n")
        os.replace(temp_file, filename)
        return True
    except OSError as error:
        print(f"Could not save {os.path.basename(filename)}: {error}")
        return False


def load_budget(filename):
    """Return the saved monthly budget, or None if no valid budget is set."""
    try:
        with open(filename, encoding="utf-8") as file:
            return parse_price(file.read())
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def save_budget(filename, amount):
    """Save a monthly budget, or delete it when amount is None. Returns True if it worked."""
    try:
        if amount is None:
            if os.path.exists(filename):
                os.remove(filename)
        else:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"{amount}\n")
        return True
    except OSError as error:
        print(f"Could not save the budget: {error}")
        return False


# ---------- Money and dates ----------
def monthly_cost(sub):
    """How much this subscription costs per month."""
    if sub["cycle"] == "yearly":
        return sub["price"] / 12
    return sub["price"]


def yearly_cost(sub):
    """How much this subscription costs per year."""
    return monthly_cost(sub) * 12


def days_until(sub):
    """Number of days from today until the next renewal."""
    return (sub["renewal"] - date.today()).days


def next_renewal(renewal, cycle):
    """Move a renewal date forward by one billing cycle."""
    year = renewal.year
    month = renewal.month
    if cycle == "yearly":
        year = year + 1
    else:
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(renewal.day, last_day))


def auto_renew(subscriptions):
    """AUTOMATION: move every renewal date that has passed to its next date."""
    renewed = 0
    for sub in subscriptions:
        if days_until(sub) < 0:
            while days_until(sub) < 0:
                sub["renewal"] = next_renewal(sub["renewal"], sub["cycle"])
            print(f"Auto-renewed {sub['name']} -> next payment {sub['renewal']}")
            renewed = renewed + 1
    return renewed


def load_and_renew():
    """Load the data file, renew old dates, and save if anything changed."""
    subscriptions = load_subscriptions(DATA_FILE)
    if auto_renew(subscriptions) > 0:
        save_subscriptions(DATA_FILE, subscriptions)
    return subscriptions


# ---------- Showing information ----------
def by_name(sub):
    return sub["name"].lower()


SORT_KEYS = {"name": by_name, "price": monthly_cost, "date": days_until}


def show_all(subscriptions):
    """Print every subscription as a table."""
    if len(subscriptions) == 0:
        print("No subscriptions to show.")
        return
    print(f"\n{'Name':<18}{'Category':<15}{'Cycle':<9}"
          f"{'Price':>10}{'Per month':>11}{'Per year':>11}{'Days':>6}")
    print("-" * 80)
    for sub in subscriptions:
        print(f"{sub['name'][:17]:<18}{sub['category']:<15}{sub['cycle']:<9}"
              f"{sub['price']:>10.2f}{monthly_cost(sub):>11.2f}"
              f"{yearly_cost(sub):>11.2f}{days_until(sub):>6}")


def show_upcoming(subscriptions, days):
    """Print the subscriptions that renew in the next few days, soonest first."""
    upcoming = []
    for sub in subscriptions:
        if days_until(sub) <= days:
            upcoming.append(sub)

    print(f"\nRenewing in the next {days} days:")
    if len(upcoming) == 0:
        print("  Nothing - relax!")
        return
    for sub in sorted(upcoming, key=days_until):
        left = days_until(sub)
        warning = ""
        if left <= WARNING_DAYS:
            warning = "  <-- SOON!"
        print(f"  {sub['name'][:17]:<18}{sub['price']:>10.2f} {CURRENCY}"
              f"   in {left} day(s)  ({sub['renewal']}){warning}")


# ---------- Report ----------
def build_report(subscriptions, budget=None):
    """Calculate the spending statistics and return them in a dictionary."""
    stats = {
        "count": len(subscriptions),
        "monthly_total": 0,
        "by_category": {},
        "most_expensive": None,
        "budget": budget,
    }
    for sub in subscriptions:
        cost = monthly_cost(sub)
        stats["monthly_total"] += cost
        totals = stats["by_category"]
        totals[sub["category"]] = totals.get(sub["category"], 0) + cost
        if stats["most_expensive"] is None or cost > monthly_cost(stats["most_expensive"]):
            stats["most_expensive"] = sub
    stats["yearly_total"] = stats["monthly_total"] * 12
    return stats


def budget_status(stats):
    """One line that says how the monthly total compares to the budget."""
    budget = stats["budget"]
    if budget is None:
        return "not set (python3 cli.py budget 3000)"
    left = budget - stats["monthly_total"]
    used = stats["monthly_total"] / budget
    if left >= 0:
        return f"{budget:.2f} {CURRENCY} - {used:.0%} used, {left:.2f} {CURRENCY} left"
    return f"{budget:.2f} {CURRENCY} - OVER BUDGET by {-left:.2f} {CURRENCY} ({used:.0%})"


def format_report(stats):
    """Turn the statistics into a readable multi-line report."""
    category_lines = ""
    for category, amount in sorted(stats["by_category"].items()):
        share = 0
        if stats["monthly_total"] > 0:
            share = amount / stats["monthly_total"]
        category_lines += f"  {category:<15}{amount:>10.2f} {CURRENCY}/month  ({share:.0%})\n"

    top = stats["most_expensive"]
    top_text = "-"
    if top is not None:
        top_text = f"{top['name']} ({monthly_cost(top):.2f} {CURRENCY}/month)"

    return f"""===== SUBSCRIPTION REPORT ({date.today()}) =====
Subscriptions:   {stats['count']}
Monthly total:   {stats['monthly_total']:.2f} {CURRENCY}
Yearly total:    {stats['yearly_total']:.2f} {CURRENCY}
Most expensive:  {top_text}
Monthly budget:  {budget_status(stats)}

Spending by category:
{category_lines}"""


def save_report(report, filename):
    """Write the report text to a file. Returns True if it worked."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report)
        return True
    except OSError as error:
        print(f"Could not save the report: {error}")
        return False


# ---------- Interactive mode: asking the user ----------
def ask_until_valid(prompt, parse_function):
    """Keep asking until parse_function accepts the answer."""
    while True:
        try:
            return parse_function(input(prompt))
        except ValueError as error:
            print(error)


def menu_add(subscriptions):
    """Ask for a new subscription, add it and save the file."""
    print("\n-- Add a subscription --")
    name = ask_until_valid("Name: ", parse_name)
    if find_subscription(subscriptions, name) is not None:
        print(f"{name} is already in your list.")
        return
    price = ask_until_valid("Price: ", parse_price)
    cycle = ask_until_valid("Billing cycle (monthly/yearly): ", parse_cycle)
    renewal = ask_until_valid("Next renewal date (YYYY-MM-DD): ", parse_date)
    add_subscription(subscriptions, name, price, cycle, renewal)
    save_subscriptions(DATA_FILE, subscriptions)
    print(f"Added {name} (category: {get_category(name)}).")


def menu_remove(subscriptions):
    """Ask for a name, remove that subscription and save the file."""
    removed = remove_subscription(subscriptions, input("Name to remove: "))
    if removed is None:
        print("No subscription with that name.")
        return
    save_subscriptions(DATA_FILE, subscriptions)
    print(f"Removed {removed['name']}.")


def menu_budget():
    """Show the budget and let the user change it (empty answer keeps it)."""
    current = load_budget(BUDGET_FILE)
    print(f"\nCurrent monthly budget: {current if current is not None else 'not set'}")
    answer = input("New budget (press Enter to keep it): ").strip()
    if answer == "":
        return
    try:
        amount = parse_price(answer)
    except ValueError as error:
        print(error)
        return
    if save_budget(BUDGET_FILE, amount):
        print(f"Budget set to {amount:.2f} {CURRENCY} per month.")


def run_menu(subscriptions, days=7):
    """Interactive mode: show the menu until the user chooses Exit."""
    while True:
        print("\n========= SUBSCRIPTION TRACKER =========")
        print("1) Show all    2) Upcoming    3) Add")
        print("4) Remove      5) Report      6) Budget    0) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            show_all(subscriptions)
        elif choice == "2":
            show_upcoming(subscriptions, days)
        elif choice == "3":
            menu_add(subscriptions)
        elif choice == "4":
            menu_remove(subscriptions)
        elif choice == "5":
            report = format_report(build_report(subscriptions, load_budget(BUDGET_FILE)))
            print("\n" + report)
            if save_report(report, REPORT_FILE):
                print("Report saved to data/report.txt")
        elif choice == "6":
            menu_budget()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 0 to 6.")


def main():
    subscriptions = load_and_renew()
    try:
        run_menu(subscriptions)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
