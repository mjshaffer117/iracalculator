import sys
from services import data

def main(arg):
    if data.is_market_active() == "OPEN":
        print(data.INTRADAY_WARNING)
        print('-' * 50)
    print(data.ACCURACY_WARNING)
    print('-' * 50)
    price = data.get_ticker_price(arg)
    status = data.is_market_active()
    print(f"Market status is: {status}.")
    try:
        print(f"Fetching data for: {arg} ...")
        price = data.get_ticker_price(arg)
        print(f"The current price for '{arg}' is: {price}")
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main("MSFT")