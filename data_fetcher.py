# fetcher.py

import requests

class CoinDCXFetcher:
    def __init__(self, symbol="BTCINR"):
        self.symbol = symbol.upper()

    def get_latest_price(self):
        url = "https://public.coindcx.com/market_data/current_prices"
        try:
            response = requests.get(url)
            data = response.json()

            if self.symbol in data:
                return float(data[self.symbol])
            else:
                print(f"[FETCH ERROR] Symbol {self.symbol} not found in response.")
                return None

        except Exception as e:
            print(f"[FETCH ERROR] {e}")
            return None
