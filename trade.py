from algo.algo import Algo
from wallet import Wallet
from utils.plotter import PlotManager
from data_fetcher import DataFetcher
import time

def main(symbol, pair):
    fetcher = DataFetcher(symbol, pair)
    wallet = Wallet()
    algo = Algo(wallet)
    plotter = PlotManager(algo)

    while True:
        data = fetcher.fetch_market_data()
        if data is not None:
            algo.decide(data.price, data.high, data.low, data.bids, data.asks, data.timestamp)
            plotter.plot()
            print(f"balance left: {wallet.fiat}, crypto: {wallet.crypto}")
        time.sleep(3) 

if __name__ == "__main__":
    main("ETHUSDT", "I-ETH_USDT")
