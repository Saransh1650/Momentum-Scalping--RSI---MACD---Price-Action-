def cci(highs, lows, closes, period=20):
    if len(highs) < period or len(lows) < period or len(closes) < period:
        print("CCI values are null")
        return None

    try:
        tp = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        sma = sum(tp[-period:]) / period
        mean_dev = sum(abs(x - sma) for x in tp[-period:]) / period
        if mean_dev == 0:
            print("CCI: mean_dev == 0:")
            return 0  # or None/50 depending on your strategy
        return (tp[-1] - sma) / (0.015 * mean_dev)
    except (TypeError, ZeroDivisionError):
        return None
