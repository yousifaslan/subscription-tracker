"""
Subscription Tracker - command-line interface

Every feature of the tracker as a command with arguments.

Examples:
    python3 cli.py list --sort price
    python3 cli.py add --name Netflix --price 229.99 --cycle monthly --renewal 2026-10-20
    python3 cli.py remove --name Netflix
    python3 cli.py upcoming --days 14
    python3 cli.py report --save
    python3 cli.py budget 3000
    python3 cli.py menu
"""

import argparse
import sys

import subscription_tracker as tracker


# ---------- Argument types (reuse the tracker's input checks) ----------
def checked(parse_function):
    """Wrap a tracker parse function so argparse shows its error message."""
    def convert(text):
        try:
            return parse_function(text)
        except ValueError as error:
            raise argparse.ArgumentTypeError(str(error))
    return convert


def parse_days(text):
    """Number of days to look ahead: a whole number from 0 to 365."""
    try:
        days = int(text)
    except ValueError:
        raise ValueError("Days must be a whole number.") from None
    if not 0 <= days <= 365:
        raise ValueError("Days must be between 0 and 365.")
    return days


def parse_budget(text):
    """A monthly budget follows the same rules as a price."""
    try:
        return tracker.parse_price(text)
    except ValueError as problem:
        raise ValueError(str(problem).replace("Price", "Budget")) from None


def error(message):
    """Print an error to stderr and return the failure exit code."""
    print(f"Error: {message}", file=sys.stderr)
    return 1


# ---------- One function per command ----------
def cmd_list(args, subscriptions):
    selected = []
    for sub in subscriptions:
        if args.category is None or sub["category"].lower() == args.category.lower():
            selected.append(sub)
    selected.sort(key=tracker.SORT_KEYS[args.sort], reverse=args.sort == "price")
    tracker.show_all(selected)
    return 0


def cmd_add(args, subscriptions):
    problem = tracker.add_subscription(subscriptions, args.name, args.price, args.cycle, args.renewal)
    if problem:
        return error(problem)
    if not tracker.save_subscriptions(tracker.DATA_FILE, subscriptions):
        return 1
    print(f"Added {args.name} ({tracker.get_category(args.name)}), "
          f"{args.price:.2f} {tracker.CURRENCY} {args.cycle}, next payment {args.renewal}.")
    return 0


def cmd_remove(args, subscriptions):
    removed = tracker.remove_subscription(subscriptions, args.name)
    if removed is None:
        return error(f"No subscription called '{args.name}'.")
    if not tracker.save_subscriptions(tracker.DATA_FILE, subscriptions):
        return 1
    print(f"Removed {removed['name']}.")
    return 0


def cmd_upcoming(args, subscriptions):
    tracker.show_upcoming(subscriptions, args.days)
    return 0


def cmd_report(args, subscriptions):
    stats = tracker.build_report(subscriptions, tracker.load_budget(tracker.BUDGET_FILE))
    report = tracker.format_report(stats)
    print(report)
    if args.save:
        if not tracker.save_report(report, tracker.REPORT_FILE):
            return 1
        print("Report saved to data/report.txt")
    return 0


def cmd_budget(args, subscriptions):
    if args.clear:
        if not tracker.save_budget(tracker.BUDGET_FILE, None):
            return 1
        print("Budget removed.")
        return 0
    if args.amount is not None:
        if not tracker.save_budget(tracker.BUDGET_FILE, args.amount):
            return 1
    stats = tracker.build_report(subscriptions, tracker.load_budget(tracker.BUDGET_FILE))
    print(f"Monthly spending: {stats['monthly_total']:.2f} {tracker.CURRENCY}")
    print(f"Monthly budget:   {tracker.budget_status(stats)}")
    return 0


def cmd_menu(args, subscriptions):
    try:
        tracker.run_menu(subscriptions, args.days)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    return 0


# ---------- Parser ----------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py", description="Track your subscriptions, renewals and monthly spending.")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p = commands.add_parser("list", help="show all subscriptions as a table")
    p.add_argument("--sort", choices=sorted(tracker.SORT_KEYS), default="date",
                   help="sort by renewal date (default), monthly price, or name")
    p.add_argument("--category", help="only show one category, e.g. Entertainment")
    p.set_defaults(func=cmd_list)

    p = commands.add_parser("add", help="add a new subscription")
    p.add_argument("--name", required=True, type=checked(tracker.parse_name))
    p.add_argument("--price", required=True, type=checked(tracker.parse_price), help="e.g. 229.99")
    p.add_argument("--cycle", required=True, type=checked(tracker.parse_cycle), help="monthly or yearly")
    p.add_argument("--renewal", required=True, type=checked(tracker.parse_date),
                   help="next payment date, YYYY-MM-DD")
    p.set_defaults(func=cmd_add)

    p = commands.add_parser("remove", help="remove a subscription by name")
    p.add_argument("--name", required=True)
    p.set_defaults(func=cmd_remove)

    p = commands.add_parser("upcoming", help="show renewals coming up soon")
    p.add_argument("--days", type=checked(parse_days), default=7, help="days to look ahead (default 7)")
    p.set_defaults(func=cmd_upcoming)

    p = commands.add_parser("report", help="spending report with totals, categories and budget")
    p.add_argument("--save", action="store_true", help="also save it to data/report.txt")
    p.set_defaults(func=cmd_report)

    p = commands.add_parser("budget", help="show or set your monthly budget")
    group = p.add_mutually_exclusive_group()
    group.add_argument("amount", nargs="?", type=checked(parse_budget), help="new monthly budget")
    group.add_argument("--clear", action="store_true", help="remove the budget")
    p.set_defaults(func=cmd_budget)

    p = commands.add_parser("menu", help="open the interactive menu")
    p.add_argument("--days", type=checked(parse_days), default=7)
    p.set_defaults(func=cmd_menu)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    subscriptions = tracker.load_and_renew()
    return args.func(args, subscriptions)


if __name__ == "__main__":
    sys.exit(main())
