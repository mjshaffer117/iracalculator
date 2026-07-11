import argparse
import logging
import shlex
import sys
from typing import Optional, Sequence

from services import data
from services import db
from services import view


def configure_logging(verbose: bool = False) -> None:
    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

        file_handler = logging.FileHandler("iracalculator.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG if verbose else logging.WARNING)
        console.setFormatter(fmt)
        root.addHandler(console)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IRA calculator CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="cmd")

    p_add = subparsers.add_parser("add", help="add (ticker) ---> Add a ticker to the database")
    p_add.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")

    p_set_alloc = subparsers.add_parser("set-allocation", help="set-allocation (ticker, percent) ---> Set allocation percent for a ticker")
    p_set_alloc.add_argument("ticker", help="Ticker symbol")
    p_set_alloc.add_argument("percent", type=float, help="Allocation percentage (e.g. 20)")

    p_set_cash = subparsers.add_parser("set-cash", help="set-cash (amount) ---> Set total buying power (cash)")
    p_set_cash.add_argument("amount", type=float, help="Amount of cash available")

    subparsers.add_parser("list", help="list ---> List tickers and allocations")

    p_compute = subparsers.add_parser("compute", help="compute [--cash AMOUNT] ---> Compute allocation amounts from cash")
    p_compute.add_argument("--cash", type=float, help="Override cash amount for this computation")

    p_price = subparsers.add_parser("price", help="price (ticker) ---> Fetch current price for a ticker")
    p_price.add_argument("ticker", help="Ticker symbol")

    subparsers.add_parser("view", help="view ---> Display all database contents")

    return parser


def execute_command(args: argparse.Namespace, exit_on_error: bool = True) -> None:
    configure_logging(getattr(args, "verbose", False))

    # ensure DB exists
    db.init_db()

    if args.cmd == "add":
        t = args.ticker.strip().upper()
        db.add_ticker(t)
        print(f"Added ticker: {t}")
    elif args.cmd == "set-allocation":
        t = args.ticker.strip().upper()
        db.set_allocation(t, args.percent)
        print(f"Set allocation for {t} to {args.percent}%")
    elif args.cmd == "set-cash":
        db.set_cash(args.amount)
        print(f"Set cash to: {args.amount}")
    elif args.cmd == "list":
        rows = db.list_tickers()
        if not rows:
            print("No tickers in database.")
            return
        for r in rows:
            print(f"{r['ticker']}: {r['allocation']}%")
    elif args.cmd == "compute":
        cash = args.cash if args.cash is not None else db.get_cash()
        if cash is None:
            print("Cash not set. Use `set-cash` or pass --cash.")
            if exit_on_error:
                sys.exit(1)
            return
        allocations = db.compute_allocations(cash=cash)
        print(f"Using cash = {cash}")
        for t, amt in allocations.items():
            print(f"{t}: {amt:.2f}")
    elif args.cmd == "price":
        t = args.ticker.strip().upper()
        try:
            price = data.get_ticker_price(t)
            print(f"The current price for '{t}' is: {price}")
        except ValueError as e:
            print(f"Error: {e}")
            if exit_on_error:
                sys.exit(1)
        except Exception:
            print("An unexpected error occurred. Check iracalculator.log for details.")
            if exit_on_error:
                sys.exit(2)
    elif args.cmd == "view":
        view.display_all()


def run_repl(parser: argparse.ArgumentParser) -> None:
    print("IRA Calculator interactive mode. Type 'help' for commands or 'quit' to exit.")
    db.init_db()

    while True:
        try:
            raw_input = input("ira> ").strip()
        except EOFError:
            print()
            break

        if not raw_input:
            continue

        if raw_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        if raw_input.lower() in {"help", "?"}:
            print("Commands: add <ticker>, set-allocation <ticker> <percent>, set-cash <amount>, list, compute [--cash AMOUNT], price <ticker>, view, help, quit")
            continue

        try:
            argv = shlex.split(raw_input)
        except ValueError as exc:
            print(f"Error: {exc}")
            continue

        if not argv:
            continue

        try:
            args = parser.parse_args(argv)
        except SystemExit:
            continue

        execute_command(args, exit_on_error=False)


def main_cli(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    argv_list = list(sys.argv[1:] if argv is None else argv)

    if not argv_list:
        run_repl(parser)
        return

    args = parser.parse_args(argv_list)
    execute_command(args)


if __name__ == "__main__":
    main_cli()