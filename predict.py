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
        self.last_bids = []
        self.last_ask = []

    def ema(self, prices, period):
        if len(prices) < period:
            return None
        ema_vals = [prices[0]]
        alpha = 2 / (period + 1)
        for price in prices[1:]:
            ema_vals.append((price - ema_vals[-1]) * alpha + ema_vals[-1])
        return ema_vals[-1]

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period:
            return None
        scaled_prices = np.array(prices) * 1e9  # scale up to make differences significant
        delta = np.diff(scaled_prices)
        gain = np.maximum(delta, 0)
        loss = np.abs(np.minimum(delta, 0))

        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        epsilon = 1e-8  # Slightly higher epsilon to ensure stability
        avg_loss = max(avg_loss, epsilon)

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))   

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        if len(prices) < slow:
            return None, None
        ema_fast = self.ema(prices[-slow:], fast)
        ema_slow = self.ema(prices[-slow:], slow)
        macd = ema_fast - ema_slow
        self.macd_vals.append(macd)
        signal_line = self.ema(self.macd_vals, signal) if len(self.macd_vals) >= signal else 0
        self.signal_vals.append(signal_line)
        return macd, signal_line

    def is_flat_market(self, window=20, threshold=0.001):
        if len(self.close_prices) < window:
            return False
        recent = self.close_prices[-window:]
        return np.std(recent) / np.mean(recent) < threshold

    def should_skip_due_to_price_stagnation(self, price):
        if self.last_trade_price is not None:
            diff = abs(price - self.last_trade_price)
            if diff / self.last_trade_price < 0.002:
                print("Skipping trade due to price stagnation")
                return True
        return False

    def get_order_book_pressure(self, bids, asks, top_n=5):
        """
        Calculate order book pressure as (sum_bid_volume - sum_ask_volume) / total_volume
        Positive => buy pressure, Negative => sell pressure
        """
        if not bids or not asks:
            print("[WARNING] Empty order book, skipping this tick.")
            return
        sum_bid_vol = sum(float(bid[1]) for bid in bids[:top_n])
        sum_ask_vol = sum(float(ask[1]) for ask in asks[:top_n])
        total_vol = sum_bid_vol + sum_ask_vol
        if total_vol == 0:
            return 0
        pressure = (sum_bid_vol - sum_ask_vol) / total_vol
        return pressure

    def decide(self, price, bids=None, asks=None, timestamp=None):
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

        if self.should_skip_due_to_price_stagnation(price):
            return

        # Calculate order book pressure if data is available
        pressure = 0
        if bids is not None and asks is not None:
            self.last_bids = bids
            self.last_ask = asks
            pressure = self.get_order_book_pressure(bids, asks)
            print(f"Order Book Pressure: {pressure:.4f}")

        # Flat Market: Reduce exposure
        if self.wallet.crypto > 0 and self.is_flat_market():
            print("Flat market detected. Selling 100% to avoid stagnation.")
            self.wallet.sell(price, amount_pct=1)
            self.last_trade_price = price
            self.sell_points.append((self.timestamps[-1], price))
            return

        # Buy Logic
        if self.wallet.fiat > 0:
            if rsi < 30 and macd > signal and pressure > 0.1:
                print("High-confidence BUY signal (with positive order book pressure)")
                self.wallet.buy(price, amount_pct=1)
                self.last_trade_price = price
                self.pending_rsi_buy = False
                self.buy_points.append((self.timestamps[-1], price))
            elif self.pending_rsi_buy and macd > signal and pressure > 0.05:
                print("Delayed BUY on MACD confirmation and mild order book pressure")
                self.wallet.buy(price, amount_pct=1)
                self.last_trade_price = price
                self.pending_rsi_buy = False
                self.buy_points.append((self.timestamps[-1], price))
            else:
                if rsi < 30:
                    self.pending_rsi_buy = True

        # Sell Logic
        if self.wallet.crypto > 0:
            if rsi > 70 and macd < signal and pressure < -0.1:
                print("High-confidence SELL signal (with negative order book pressure)")
                self.wallet.sell(price, amount_pct=1)
                self.last_trade_price = price
                self.pending_rsi_sell = False
                self.sell_points.append((self.timestamps[-1], price))
            elif self.pending_rsi_sell and macd < signal and pressure < -0.05:
                print("Delayed SELL on MACD confirmation and mild order book pressure")
                self.wallet.sell(price, amount_pct=1)
                self.last_trade_price = price
                self.pending_rsi_sell = False
                self.sell_points.append((self.timestamps[-1], price))
            else:
                if rsi > 70:
                    self.pending_rsi_sell = True

    def plot(self):
        if not self.rsi_vals or not self.macd_vals or not self.signal_vals:
            return

        num_subplots = 4 if self.last_bids and self.last_ask else 3
        plt.figure(1, figsize=(14, 10))
        plt.clf()

        # 1. Price Chart
        plt.subplot(num_subplots, 1, 1)
        plt.plot(self.timestamps, self.close_prices, label="Price", color='black')
        buy_x, buy_y = zip(*self.buy_points) if self.buy_points else ([], [])
        sell_x, sell_y = zip(*self.sell_points) if self.sell_points else ([], [])
        plt.scatter(buy_x, buy_y, label="Buy", color='green', marker='^')
        plt.scatter(sell_x, sell_y, label="Sell", color='red', marker='v')
        plt.title("Price Movement")
        plt.legend()

        # 2. RSI
        plt.subplot(num_subplots, 1, 2)
        rsi_x = self.timestamps[-len(self.rsi_vals):]
        rsi_clean = [float(val) if val is not None else np.nan for val in self.rsi_vals]
        plt.plot(rsi_x, rsi_clean, label="RSI", color='blue')
        plt.axhline(70, color='red', linestyle='--')
        plt.axhline(30, color='green', linestyle='--')
        plt.title("RSI")
        plt.legend()

        # 3. MACD
        plt.subplot(num_subplots, 1, 3)
        macd_x = self.timestamps[-len(self.macd_vals):]
        signal_trimmed = self.signal_vals[-len(self.macd_vals):]
        plt.plot(macd_x, self.macd_vals, label="MACD", color='purple')
        plt.plot(macd_x, signal_trimmed, label="Signal", color='orange')
        plt.title("MACD and Signal")
        plt.legend()

        # 4. Order Book Depth
        if self.last_bids and self.last_ask:
            bids = sorted(self.last_bids, key=lambda x: x[0], reverse=True)
            asks = sorted(self.last_ask, key=lambda x: x[0])
            bid_prices = [float(b[0]) for b in bids]
            bid_vols = [float(b[1]) for b in bids]
            ask_prices = [float(a[0]) for a in asks]
            ask_vols = [float(a[1]) for a in asks]
            bid_cum = np.cumsum(bid_vols)
            ask_cum = np.cumsum(ask_vols)

            plt.subplot(num_subplots, 1, 4)
            plt.plot(bid_prices, bid_cum, label="Bids", color='green')
            plt.plot(ask_prices, ask_cum, label="Asks", color='red')
            plt.title("Order Book Depth")
            plt.xlabel("Price")
            plt.ylabel("Cumulative Volume")
            plt.legend()

        plt.tight_layout()
        plt.pause(0.001)

