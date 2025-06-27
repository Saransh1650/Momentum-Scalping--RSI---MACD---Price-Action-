import matplotlib.pyplot as plt
import numpy as np
plt.style.use('dark_background')

class PlotManager:
    def __init__(self, algo):
        self.algo = algo
        plt.ion()
        plt.figure(1, figsize=(16, 14))

    def plot(self):
        if not self.algo.rsi_vals or not self.algo.macd_vals or not self.algo.signal_vals:
            return

        plt.clf()
        timestamps = self.algo.timestamps

        # Subplot 1: Price Chart with Bollinger Bands
        plt.subplot(6, 1, 1)
        plt.plot(timestamps, self.algo.close_prices, label="Price", color='yellow')
        buy_x, buy_y = zip(*self.algo.buy_points) if self.algo.buy_points else ([], [])
        sell_x, sell_y = zip(*self.algo.sell_points) if self.algo.sell_points else ([], [])
        plt.scatter(buy_x, buy_y, label="Buy", color='green', marker='^')
        plt.scatter(sell_x, sell_y, label="Sell", color='red', marker='v')

        if hasattr(self.algo, 'boll_mid') and hasattr(self.algo, 'boll_upper') and hasattr(self.algo, 'boll_lower'):
            min_len = min(len(timestamps), len(self.algo.boll_mid), len(self.algo.boll_upper), len(self.algo.boll_lower))
            if min_len > 0:
                plt.plot(timestamps[-min_len:], self.algo.boll_mid[-min_len:], color='gray', linestyle='--', label="BB Mid")
                plt.plot(timestamps[-min_len:], self.algo.boll_upper[-min_len:], color='blue', linestyle='--', label="BB Upper")
                plt.plot(timestamps[-min_len:], self.algo.boll_lower[-min_len:], color='blue', linestyle='--', label="BB Lower")

        plt.title("Price with Bollinger Bands")
        plt.legend()

        # Subplot 2: RSI
        plt.subplot(6, 1, 2)
        rsi_clean = [float(val) if val is not None else np.nan for val in self.algo.rsi_vals]
        min_len = min(len(timestamps), len(rsi_clean))
        if min_len > 0:
            plt.plot(timestamps[-min_len:], rsi_clean[-min_len:], label="RSI", color='blue')
            plt.axhline(70, color='red', linestyle='--')
            plt.axhline(30, color='green', linestyle='--')
            plt.title("RSI")
            plt.legend()

        # Subplot 3: MACD & Signal
        plt.subplot(6, 1, 3)
        min_len = min(len(timestamps), len(self.algo.macd_vals), len(self.algo.signal_vals))
        if min_len > 0:
            plt.plot(timestamps[-min_len:], self.algo.macd_vals[-min_len:], label="MACD", color='purple')
            plt.plot(timestamps[-min_len:], self.algo.signal_vals[-min_len:], label="Signal", color='orange')
            plt.title("MACD and Signal")
            plt.legend()

        # Subplot 4: Stochastic Oscillator
        if hasattr(self.algo, 'stoch_k') and hasattr(self.algo, 'stoch_d'):
            min_len = min(len(timestamps), len(self.algo.stoch_k), len(self.algo.stoch_d))
            if min_len > 0:
                plt.subplot(6, 1, 4)
                plt.plot(timestamps[-min_len:], self.algo.stoch_k[-min_len:], label="%K", color='brown')
                plt.plot(timestamps[-min_len:], self.algo.stoch_d[-min_len:], label="%D", color='pink')
                plt.axhline(80, color='red', linestyle='--')
                plt.axhline(20, color='green', linestyle='--')
                plt.title("Stochastic Oscillator")
                plt.legend()

        # Subplot 5: CCI & ADX
        if hasattr(self.algo, 'cci_vals') and hasattr(self.algo, 'adx_vals'):
            min_len = min(len(timestamps), len(self.algo.cci_vals), len(self.algo.adx_vals))
            if min_len > 0:
                plt.subplot(6, 1, 5)
                plt.plot(timestamps[-min_len:], self.algo.cci_vals[-min_len:], label="CCI", color='darkcyan')
                plt.axhline(100, color='red', linestyle='--')
                plt.axhline(-100, color='green', linestyle='--')
                plt.twinx()
                plt.plot(timestamps[-min_len:], self.algo.adx_vals[-min_len:], label="ADX", color='gold')
                plt.title("CCI & ADX")
                plt.legend(loc="upper left")

        # Subplot 6: Order Book Depth
        if self.algo.last_bids and self.algo.last_ask:
            bids = sorted(self.algo.last_bids, key=lambda x: x[0], reverse=True)
            asks = sorted(self.algo.last_ask, key=lambda x: x[0])
            bid_prices = [float(b[0]) for b in bids]
            bid_vols = [float(b[1]) for b in bids]
            ask_prices = [float(a[0]) for a in asks]
            ask_vols = [float(a[1]) for a in asks]
            bid_cum = np.cumsum(bid_vols)
            ask_cum = np.cumsum(ask_vols)

            plt.subplot(6, 1, 6)
            plt.plot(bid_prices, bid_cum, label="Bids", color='green')
            plt.plot(ask_prices, ask_cum, label="Asks", color='red')
            plt.title("Order Book Depth")
            plt.xlabel("Price")
            plt.ylabel("Cumulative Volume")
            plt.legend()

        plt.tight_layout()
        plt.pause(0.001)

