import requests

class CoinDCXFetcher:
    def __init__(self, symbol="BTCINR"):
        self.symbol = symbol

    def get_latest_price(self):
        url = "https://public.coindcx.com/market_data/current_prices"
        try:
            response = requests.get(url)
            data = response.json()

            if self.symbol.upper() in data:
                return float(data[self.symbol.upper()])
            else:
                print(f"[FETCH ERROR] Symbol {self.symbol.upper()} not found in response.")
                return None

        except Exception as e:
            print(f"[FETCH ERROR] {e}")
            return None

class CoinDCXOrderBookFetcher:
    def __init__(self, symbol="BTCINR", pair="B-BTC_USDT"):
        self.symbol = symbol
        self.pair = pair

    def get_order_book(self):
        url = f"https://public.coindcx.com/market_data/orderbook?pair={self.pair}"
        try:
            response = requests.get(url)
            data = response.json()

            # bids and asks are dicts with string keys; convert to list of [price, quantity]
            bids_dict = data.get("bids", {})
            asks_dict = data.get("asks", {})

            bids = [[float(price), float(quantity)] for price, quantity in bids_dict.items()]
            asks = [[float(price), float(quantity)] for price, quantity in asks_dict.items()]

            # sort: bids (high to low), asks (low to high)
            bids.sort(reverse=True)
            asks.sort()

            return bids, asks
        except Exception as e:
            print(f"[ORDER BOOK FETCH ERROR] {e}")
            return [], []
