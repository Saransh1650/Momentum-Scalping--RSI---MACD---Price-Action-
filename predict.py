import numpy as np

class Algo:
    def __init__(self, wallet):
        self.wallet = wallet
        self.prices = []
        self.close_prices = []
        self.macd_vals = []
        self.signal_vals = []

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period:
            return None
        delta = np.diff(prices)
        gain = np.maximum(delta, 0)
        loss = np.abs(np.minimum(delta, 0))
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        if len(prices) < slow:
            return None, None
        ema_fast = np.mean(prices[-fast:])
        ema_slow = np.mean(prices[-slow:])
        macd = ema_fast - ema_slow
        self.macd_vals.append(macd)
        if len(self.macd_vals) >= signal:
            signal_line = np.mean(self.macd_vals[-signal:])
        else:
            signal_line = 0
        self.signal_vals.append(signal_line)
        return macd, signal_line

    def decide(self, price):
        self.close_prices.append(price)
        if len(self.close_prices) < 30:
            return  # wait for more data

        rsi = self.calculate_rsi(self.close_prices)
        macd, signal = self.calculate_macd(self.close_prices)
        print(f"Price: {price}, RSI: {rsi:.2f}, MACD: {macd:.4f}, Signal: {signal:.4f}")

        if rsi is None or macd is None:
            return

        # Simple scalping conditions
        if rsi < 30 and macd > signal:
            self.wallet.buy(price, amount_pct=0.1)
        elif rsi > 70 and macd < signal:
            self.wallet.sell(price, amount_pct=0.1)
