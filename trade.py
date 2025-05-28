import time
from wallet import Wallet
from predict import Algo
from data_fetcher import CoinDCXFetcher 

wallet = Wallet(initial_balance=1000)
algo = Algo(wallet)
fetcher = CoinDCXFetcher(symbol="OPUSDT")
while True:
    price = fetcher.get_latest_price()  
    if price:
        print(price)
        algo.decide(price)
        wallet.summary(price)
        algo.plot()
    time.sleep(2)