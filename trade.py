from data_fetcher import CoinDCXFetcher, CoinDCXOrderBookFetcher
from predict import Algo
from wallet import Wallet

def main(symbol, pair):
    fetcher_price = CoinDCXFetcher(symbol)
    fetcher_orderbook = CoinDCXOrderBookFetcher(symbol, pair)
    wallet = Wallet()
    algo = Algo(wallet)

    import time
    while True:
        price = fetcher_price.get_latest_price()
        bids, asks = fetcher_orderbook.get_order_book()
        if price is not None:
            algo.decide(price, bids, asks)
            print(f"Current Price: {price:.2f}, Crypto: {wallet.crypto:.6f}, Fiat: {wallet.fiat:.2f}")
            algo.plot()
        time.sleep(10) 

if __name__ == "__main__":
    main("VINUUSDT", "I-VINU_USDT")
