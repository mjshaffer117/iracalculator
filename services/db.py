import sqlite3
from typing import Dict, List, Optional

DB_PATH = "iracalculator.db"


def _get_conn(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = _get_conn(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickers (
            ticker TEXT PRIMARY KEY,
            allocation REAL DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.commit()
    return conn


def add_ticker(ticker: str, path: str = DB_PATH) -> None:
    conn = init_db(path)
    conn.execute("INSERT OR IGNORE INTO tickers(ticker, allocation) VALUES (?, 0)", (ticker,))
    conn.commit()


def set_allocation(ticker: str, percent: float, path: str = DB_PATH) -> None:
    conn = init_db(path)
    conn.execute("INSERT OR IGNORE INTO tickers(ticker, allocation) VALUES (?, 0)", (ticker,))
    conn.execute("UPDATE tickers SET allocation = ? WHERE ticker = ?", (percent, ticker))
    conn.commit()


def set_cash(amount: float, path: str = DB_PATH) -> None:
    conn = init_db(path)
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES ('cash', ?)", (str(amount),))
    conn.commit()


def get_cash(path: str = DB_PATH) -> Optional[float]:
    conn = init_db(path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='cash'")
    row = cur.fetchone()
    if row is None:
        return None
    try:
        return float(row["value"])
    except Exception:
        return None


def list_tickers(path: str = DB_PATH) -> List[sqlite3.Row]:
    conn = init_db(path)
    cur = conn.cursor()
    cur.execute("SELECT ticker, allocation FROM tickers ORDER BY ticker")
    return cur.fetchall()


def compute_allocations(cash: Optional[float] = None, path: str = DB_PATH) -> Dict[str, float]:
    if cash is None:
        cash = get_cash(path) or 0.0
    rows = list_tickers(path)
    total_percent = sum(r["allocation"] for r in rows)
    if total_percent == 0:
        return {r["ticker"]: 0.0 for r in rows}
    allocations: Dict[str, float] = {}
    for r in rows:
        allocations[r["ticker"]] = cash * (r["allocation"] / total_percent)
    return allocations
