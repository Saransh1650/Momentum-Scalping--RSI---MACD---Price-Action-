import numpy as np
import matplotlib.pyplot as plt
from decimal import getcontext

plt.ion()
getcontext().prec = 10

class Algo:
    def __init__(self, wallet):
        self.wallet = wallet
        self.close_prices = []
        self.macd_vals = []
        self.signal_vals = []
        self.rsi_vals = []
        self.timestamps = []
        self.last_trade_price = None
        self.pending_rsi_buy = False
        self.pending_rsi_sell = False
        self.buy_points = []
        self.sell_points = []

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period:
            return None
        delta = np.diff(prices)
        gain = np.maximum(delta, 0)
        loss = np.abs(np.minimum(delta, 0))
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        if len(prices) < slow:
            return None, None
        ema_fast = np.mean(prices[-fast:])
        ema_slow = np.mean(prices[-slow:])
        macd = ema_fast - ema_slow
        self.macd_vals.append(macd)
        signal_line = np.mean(self.macd_vals[-signal:]) if len(self.macd_vals) >= signal else 0
        self.signal_vals.append(signal_line)
        return macd, signal_line

    def is_flat_market(self, window=20, threshold=0.0005):
        if len(self.close_prices) < window:
            return False
        recent = self.close_prices[-window:]
        return np.std(recent) / np.mean(recent) < threshold

    def should_skip_due_to_price_stagnation(self, price):
        if self.last_trade_price is not None:
            if abs(price - self.last_trade_price) < 0.01:
                print("Skipping trade due to price stagnation")
                return True
        return False

    def decide(self, price, timestamp=None):
        self.close_prices.append(price)
        self.timestamps.append(timestamp if timestamp is not None else len(self.close_prices))

        if len(self.close_prices) < 30:
            return

        rsi = self.calculate_rsi(self.close_prices)
        macd, signal = self.calculate_macd(self.close_prices)
        self.rsi_vals.append(rsi if rsi is not None else np.nan)

        print(f"Price: {price:.2f}, RSI: {rsi:.2f}, MACD: {macd:.4f}, Signal: {signal:.4f}")

        if rsi is None or macd is None:
            return

        # if self.should_skip_due_to_price_stagnation(price):
        #     return

        if self.wallet.crypto > 0 and self.is_flat_market():
            print(f"Detected flat market. Selling all at price {price}")
            self.wallet.sell(price, amount_pct=1.0)
            self.last_trade_price = price
            self.sell_points.append((self.timestamps[-1], price))
            return

        # Buy logic
        if rsi < 30:
            if macd > signal:
                print("High-confidence BUY signal")
                self.wallet.buy(price, amount_pct=0.1)
                self.last_trade_price = price
                self.pending_rsi_buy = False
                self.buy_points.append((self.timestamps[-1], price))
            else:
                self.pending_rsi_buy = True
        elif self.pending_rsi_buy and macd > signal:
            print("Delayed BUY on MACD confirmation")
            self.wallet.buy(price, amount_pct=0.05)
            self.last_trade_price = price
            self.pending_rsi_buy = False
            self.buy_points.append((self.timestamps[-1], price))

        # Sell logic
        if rsi > 70:
            if macd < signal:
                print("High-confidence SELL signal")
                self.wallet.sell(price, amount_pct=0.1)
                self.last_trade_price = price
                self.pending_rsi_sell = False
                self.sell_points.append((self.timestamps[-1], price))
            else:
                self.pending_rsi_sell = True
        elif self.pending_rsi_sell and macd < signal:
            print("Delayed SELL on MACD confirmation")
            self.wallet.sell(price, amount_pct=0.05)
            self.last_trade_price = price
            self.pending_rsi_sell = False
            self.sell_points.append((self.timestamps[-1], price))

    def plot(self):
        if not self.rsi_vals or not self.macd_vals or not self.signal_vals:
            return

        plt.figure(1, figsize=(14, 8))
        plt.clf()

        plt.subplot(3, 1, 1)
        plt.plot(self.timestamps, self.close_prices, label="Price", color='black')
        buy_x, buy_y = zip(*self.buy_points) if self.buy_points else ([], [])
        sell_x, sell_y = zip(*self.sell_points) if self.sell_points else ([], [])
        plt.scatter(buy_x, buy_y, label="Buy", color='green', marker='^')
        plt.scatter(sell_x, sell_y, label="Sell", color='red', marker='v')
        plt.title("Price Movement")
        plt.legend()

        plt.subplot(3, 1, 2)
        rsi_x = self.timestamps[-len(self.rsi_vals):]
        rsi_clean = [float(val) if val is not None else np.nan for val in self.rsi_vals]
        plt.plot(rsi_x, rsi_clean, label="RSI", color='blue')
        plt.axhline(70, color='red', linestyle='--', linewidth=1)
        plt.axhline(30, color='green', linestyle='--', linewidth=1)
        plt.title("RSI")
        plt.legend()

        plt.subplot(3, 1, 3)
        macd_x = self.timestamps[-len(self.macd_vals):]
        signal_trimmed = self.signal_vals[-len(self.macd_vals):]
        plt.plot(macd_x, self.macd_vals, label="MACD", color='purple')
        plt.plot(macd_x, signal_trimmed, label="Signal", color='orange')
        plt.title("MACD and Signal")
        plt.legend()

        plt.tight_layout()
        plt.pause(0.001)
