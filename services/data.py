import logging

import requests

ACCURACY_WARNING = (
    "WARNING: Market data is open-source (yfinance) and not guaranteed. "
    "Use caution when executing real financial transactions."
)

INTRADAY_WARNING = (
    "NOTICE: The stock market is currently open. yfinance intraday data "
    "is delayed by 15 minutes. Mutual Fund prices will reflect yesterday's close."
)

logger = logging.getLogger(__name__)

def is_market_active() -> str:
    """Return 'OPEN', 'CLOSED', or 'ERROR' indicating US market status."""
    try:
        import yfinance as yf
    except ImportError:
        logger.exception("yfinance is not installed; unable to determine market status")
        return "ERROR"

    try:
        US = yf.Market("US")
        market_info = US.status
        market_state = market_info.get("marketState", "UNKNOWN")
        if market_state == "REGULAR":
            return "OPEN"
        else:
            return "CLOSED"
    except Exception:
        logger.exception("Unable to determine market status")
        return "ERROR"


def get_ticker_price(ticker: str) -> float:
    """Fetch the most recent close price for `ticker`.

    Raises ValueError when the ticker is not found or data cannot be fetched.
    """
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ValueError("yfinance is not installed. Install it to use the price command.") from exc

    ticker = ticker.strip().upper()
    ticker_obj = yf.Ticker(ticker)
    try:
        data = ticker_obj.history(period="1d")
    except requests.exceptions.RequestException as e:
        logger.exception("Network/HTTP error fetching history for %s", ticker)
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 404:
            raise ValueError(f"Ticker '{ticker}' was not found.") from e
        raise ValueError(f"Failed to fetch data for ticker '{ticker}': {e}") from e
    except Exception as e:
        logger.exception("Unexpected error fetching history for %s", ticker)
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 404:
            raise ValueError(f"Ticker '{ticker}' was not found.") from e
        raise ValueError(f"Failed to fetch data for ticker '{ticker}': {e}") from e

    if data.empty:
        raise ValueError(f"Ticker '{ticker}' was not found.")

    price = data["Close"].iloc[-1]
    return float(price)
