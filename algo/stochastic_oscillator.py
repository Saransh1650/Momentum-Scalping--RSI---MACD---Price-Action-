from utils.flattener import flatten


def stochastic_oscillator(highs, lows, closes, k_period=14, d_period=3):
    if len(highs) < k_period or len(lows) < k_period or len(closes) < k_period:
        print("Stochastic values are null")
        return None, None

    highs = [flatten(h) for h in highs]
    lows = [flatten(l) for l in lows]
    closes = [flatten(c) for c in closes]

    high_k_max = max(highs[-k_period:])
    low_k_min = min(lows[-k_period:])
    current_close = closes[-1]

    denominator = high_k_max - low_k_min
    k = 0 if denominator == 0 else 100 * (current_close - low_k_min) / denominator

    # Compute full %K history for %D
    k_values = []
    for i in range(-k_period - d_period + 1, 1):
        sub_highs = highs[i - k_period + 1:i + 1]
        sub_lows = lows[i - k_period + 1:i + 1]
        sub_close = closes[i]
        if len(sub_highs) < k_period or len(sub_lows) < k_period:
            continue
        max_h = max(sub_highs)
        min_l = min(sub_lows)
        denom = max_h - min_l
        k_val = 0 if denom == 0 else 100 * (sub_close - min_l) / denom
        k_values.append(k_val)

    if len(k_values) < d_period:
        return k, None

    d = sum(k_values[-d_period:]) / d_period
    return k, d
