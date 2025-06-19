import requests
from market_data import MarketData
import datetime
from typing import List, Optional, Tuple
class DataFetcher:
    def __init__(self, symbol: str = "BTCINR", pair: str = "B-BTC_USDT"):
        self.symbol = symbol.upper()
        self.pair = pair

    def fetch_market_data(self) -> MarketData:
        price, high, low, volume = self._fetch_ticker_data()
        bids, asks = self._fetch_order_book()
        timestamp=datetime.datetime.now()
        return MarketData(
            price=price,
            high=high,
            low=low,
            volume=volume,
            bids=bids,
            asks=asks,
            timestamp=timestamp
        )

    def _fetch_ticker_data(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        url = "https://api.coindcx.com/exchange/ticker"
        try:
            response = requests.get(url)
            data = response.json()
            for item in data:
                if item["market"] == self.symbol:
                    return (
                        float(item["last_price"]),
                        float(item["high"]),
                        float(item["low"]),
                        float(item["volume"])
                    )
            print(f"[TICKER ERROR] {self.symbol} not found.")
            return None, None, None, None
        except Exception as e:
            print(f"[TICKER FETCH ERROR] {e}")
            return None, None, None, None

    def _fetch_order_book(self) -> Tuple[List[List[float]], List[List[float]]]:
        url = f"https://public.coindcx.com/market_data/orderbook?pair={self.pair}"
        try:
            response = requests.get(url)
            data = response.json()

            bids_dict = data.get("bids", {})
            asks_dict = data.get("asks", {})

            bids = [[float(price), float(quantity)] for price, quantity in bids_dict.items()]
            asks = [[float(price), float(quantity)] for price, quantity in asks_dict.items()]

            bids.sort(reverse=True)
            asks.sort()

            return bids, asks
        except Exception as e:
            print(f"[ORDER BOOK FETCH ERROR] {e}")
            return [], []
