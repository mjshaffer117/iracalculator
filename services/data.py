import yfinance as yf

ACCURACY_WARNING = (
    "WARNING: Market data is open-source (yfinance) and not guaranteed. "
    "Use caution when executing real financial transactions."
)

INTRADAY_WARNING = (
    "NOTICE: The stock market is currently open. yfinance intraday data "
    "is delayed by 15 minutes. Mutual Fund prices will reflect yesterday's close."
)

def is_market_active():
    try:
        US = yf.Market("US")
        market_info = US.status
        state = market_info.get("marketState", "UNKNOWN") == "REGULAR"
        if state == "REGULAR":
            return "OPEN"
        else:
            return "CLOSED"
    except Exception:
        return "ERROR"

def get_ticker_price(ticker: str) -> float:
    ticker = ticker.strip().upper()
    object = yf.Ticker(ticker)
    data = object.history(period="1d")
    if data.empty:
        raise ValueError(f"Ticker '{ticker}' was not found.")
    price = data["Close"].iloc[-1]
    return float(price)
