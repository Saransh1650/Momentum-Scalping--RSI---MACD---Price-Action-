import numpy as np

def ema(prices, period):
    if len(prices) < period:
        return None
    ema_vals = [prices[0]]
    alpha = 2 / (period + 1)
    for price in prices[1:]:
        ema_vals.append((price - ema_vals[-1]) * alpha + ema_vals[-1])
    return ema_vals[-1]

def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return None
    scaled_prices = np.array(prices) * 1e9
    delta = np.diff(scaled_prices)
    gain = np.maximum(delta, 0)
    loss = np.abs(np.minimum(delta, 0))

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    avg_loss = max(avg_loss, 1e-8)

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, macd_vals, fast=12, slow=26, signal=9):
    if len(prices) < slow:
        return None, None
    ema_fast = ema(prices[-slow:], fast)
    ema_slow = ema(prices[-slow:], slow)
    macd = ema_fast - ema_slow
    macd_vals.append(macd)
    signal_line = ema(macd_vals, signal) if len(macd_vals) >= signal else 0
    return macd, signal_line

def is_flat_market(close_prices, window=20, threshold=0.001):
    if len(close_prices) < window:
        return False
    recent = close_prices[-window:]
    return np.std(recent) / np.mean(recent) < threshold

def get_trend_direction(prices, fast=10, slow=50):
    if len(prices) < slow:
        return None
    fast_ema = ema(prices[-slow:], fast)
    slow_ema = ema(prices[-slow:], slow)
    if fast_ema > slow_ema:
        return 'uptrend'
    elif fast_ema < slow_ema:
        return 'downtrend'
    return 'sideways'
