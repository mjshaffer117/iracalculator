"""Display database contents in a formatted table."""

from services import db


def display_all() -> None:
    """Print tickers, allocations, and settings from the database."""
    print("\n=== TICKERS ===")
    rows = db.list_tickers()
    if not rows:
        print("  (none)")
    else:
        print(f"  {'Ticker':<10} {'Allocation':<15}")
        print(f"  {'-' * 10} {'-' * 15}")
        for r in rows:
            print(f"  {r['ticker']:<10} {r['allocation']:<15}%")

    print("\n=== SETTINGS ===")
    cash = db.get_cash()
    if cash is None:
        print("  Cash: (not set)")
    else:
        print(f"  Cash: ${cash:,.2f}")

    print()
