def atr(highs, lows, closes, period=14):
    if not highs or not lows or not closes:
        print("ATR input values are null")
        return None

    if len(closes) < period + 1:
        print("len(closes) < period + 1: ATR")
        return None

    highs = highs[-(period + 1):]
    lows = lows[-(period + 1):]
    closes = closes[-(period + 1):]

    tr = []
    for i in range(1, len(closes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i - 1])
        low_close = abs(lows[i] - closes[i - 1])
        tr.append(max(high_low, high_close, low_close))

    atr_vals = [sum(tr[:period]) / period]
    for val in tr[period:]:
        atr_vals.append((atr_vals[-1] * (period - 1) + val) / period)

    return atr_vals[-1] if atr_vals else None
