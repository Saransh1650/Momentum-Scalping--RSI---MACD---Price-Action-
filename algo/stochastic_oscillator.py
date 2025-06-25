from utils.flattener import flatten


def stochastic_oscillator(highs, lows, closes, k_period=14, d_period=3):
    if len(highs) < k_period or len(lows) < k_period or len(closes) < k_period:
        print("Stochastic values are null")
        return None, None

    highs = [flatten(h) for h in highs]
    lows = [flatten(l) for l in lows]
    closes = [flatten(c) for c in closes]

    # %K for current value
    high_k_max = max(highs[-k_period:])
    low_k_min = min(lows[-k_period:])
    current_close = closes[-1]

    denominator = high_k_max - low_k_min
    k = 0 if denominator == 0 else 100 * (current_close - low_k_min) / denominator

    # %D: SMA of last d_period %K values
    k_values = []
    for j in range(d_period):
        if len(highs) < k_period + j:
            continue
        window_highs = highs[-k_period - j:-j or None]
        window_lows = lows[-k_period - j:-j or None]
        window_closes = closes[-k_period - j:-j or None]
        if not window_closes:
            continue
        window_close = window_closes[-1]  # latest in that window

        high_max = max(window_highs)
        low_min = min(window_lows)
        denom = high_max - low_min
        k_val = 0 if denom == 0 else 100 * (window_close - low_min) / denom
        k_values.append(k_val)

    if len(k_values) < d_period:
        return k, None

    d = sum(k_values) / len(k_values)
    return k, d
