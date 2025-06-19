from algo.atr import atr
from algo.adx import adx
from algo.bollinger_bands import bollinger_bands
from algo.cci import cci
from algo.stochastic_oscillator import stochastic_oscillator
from algo.indicators import calculate_rsi, calculate_macd, is_flat_market
from algo.orderbook import get_order_book_pressure
import numpy as np
from utils.logger import fmt
import datetime

class Algo:
    def __init__(self, wallet):
        self.wallet = wallet
        self.close_prices = []
        self.highs = []
        self.lows = []
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
        self.atr_vals = []
        self.adx_vals = []
        self.cci_vals = []
        self.stoch_k = []
        self.stoch_d = []
        self.boll_mid = []
        self.boll_upper = []
        self.boll_lower = []

    def should_skip_due_to_price_stagnation(self, price):
        if self.last_trade_price is not None:
            diff = abs(price - self.last_trade_price)
            if diff / self.last_trade_price < 0.002:
                print("Skipping trade due to price stagnation")
                return True
        return False    

    def decide(self, price, high=None, low=None, bids=None, asks=None, timestamp=None):
        self.close_prices.append(price)
        if high is not None:
            self.highs.append(high)
        if low is not None:
            self.lows.append(low)
        self.timestamps.append(timestamp or datetime.datetime.now())

        # Ensure enough data for indicators
        if len(self.close_prices) < 50 or len(self.highs) < 50 or len(self.lows) < 50:
            return

        # Base indicators
        rsi = calculate_rsi(self.close_prices)
        macd, signal = calculate_macd(self.close_prices, self.macd_vals)
        self.signal_vals.append(signal)
        self.rsi_vals.append(rsi or np.nan)

        # Advanced indicators
        atr_val = atr(self.highs, self.lows, self.close_prices)
        adx_val = adx(self.highs, self.lows, self.close_prices)
        mid_bb, upper_bb, lower_bb = bollinger_bands(self.close_prices)
        cci_val = cci(self.highs, self.lows, self.close_prices)
        stoch_k, stoch_d = stochastic_oscillator(self.highs, self.lows, self.close_prices)

        self.adx_vals.append(adx_val if adx_val is not None else np.nan)
        self.cci_vals.append(cci_val if cci_val is not None else np.nan)
        self.stoch_k.append(stoch_k if stoch_k is not None else np.nan)
        self.stoch_d.append(stoch_d if stoch_d is not None else np.nan)
        self.boll_mid.append(mid_bb if mid_bb is not None else np.nan)
        self.boll_upper.append(upper_bb if upper_bb is not None else np.nan)
        self.boll_lower.append(lower_bb if lower_bb is not None else np.nan)

        if bids and asks:
            self.last_bids = bids
            self.last_ask = asks

        print(f"P:{price:.2f} "
              f"RSI:{fmt(rsi,1)} MACD:{fmt(macd,4)}/{fmt(signal,4)} "
              f"ATR:{fmt(atr_val,3)} ADX:{fmt(adx_val,1)} CCI:{fmt(cci_val,1)} "
              f"%K/D:{fmt(stoch_k,1)}/{fmt(stoch_d,1)}")

        if None in (rsi, macd, atr_val, adx_val, stoch_k):
            return
        if self.should_skip_due_to_price_stagnation(price):
            return

        pressure = get_order_book_pressure(bids, asks) if bids and asks else 0
        print(f"Pressure:{pressure:.3f}")

        # Exit logic
        if self.wallet.crypto > 0 and (is_flat_market(self.close_prices) or adx_val < 20):
            print("Flat or weak trend. Selling full position.")
            self.wallet.sell(price, amount_pct=1)
            self.last_trade_price = price
            self.sell_points.append((self.timestamps[-1], price))
            return

        # Buy logic
        if self.wallet.fiat > 0:
            if (rsi < 30 and macd > signal and pressure > 0.1 and
                price < lower_bb and stoch_k < 20 and adx_val > 25):
                print("Strong BUY signal.")
                self.wallet.buy(price, amount_pct=1)
                self._record_buy(price)
            elif self.pending_rsi_buy and macd > signal and pressure > 0.05:
                print("Delayed BUY.")
                self.wallet.buy(price, amount_pct=1)
                self._record_buy(price)
            elif rsi < 30:
                self.pending_rsi_buy = True

        # Sell logic
        if self.wallet.crypto > 0:
            if (rsi > 70 and macd < signal and pressure < -0.1 and
                price > upper_bb and stoch_k > 80 and adx_val > 25):
                print("Strong SELL signal.")
                self.wallet.sell(price, amount_pct=1)
                self._record_sell(price)
            elif self.pending_rsi_sell and macd < signal and pressure < -0.05:
                print("Delayed SELL.")
                self.wallet.sell(price, amount_pct=1)
                self._record_sell(price)
            elif rsi > 70:
                self.pending_rsi_sell = True

        self._trim()

    def _record_buy(self, price):
        self.last_trade_price = price
        self.pending_rsi_buy = False
        self.buy_points.append((self.timestamps[-1], price))

    def _record_sell(self, price):
        self.last_trade_price = price
        self.pending_rsi_sell = False
        self.sell_points.append((self.timestamps[-1], price))

    def _trim(self):
        MAX_LENGTH = 300
        for attr in [
            'close_prices', 'highs', 'lows', 'macd_vals', 'signal_vals', 'rsi_vals',
            'adx_vals', 'cci_vals', 'stoch_k', 'stoch_d',
            'boll_mid', 'boll_upper', 'boll_lower', 'timestamps'
        ]:
            lst = getattr(self, attr, None)
            if isinstance(lst, list) and len(lst) > MAX_LENGTH:
                setattr(self, attr, lst[-MAX_LENGTH:])
