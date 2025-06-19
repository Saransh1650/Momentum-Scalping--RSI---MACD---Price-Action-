def adx(highs, lows, closes, period=14):
    if not highs or not lows or not closes:
        print("ADX ERROR: One or more input lists are None or empty.")
        return None

    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        print(f"ADX ERROR: Not enough data. highs={len(highs)}, lows={len(lows)}, closes={len(closes)}")
        return None

    plus_dm, minus_dm, tr = [], [], []

    for i in range(1, len(highs)):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]

        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)

        true_range = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        tr.append(true_range)

    def smooth(vals):
        if len(vals) < period:
            print("ADX SMOOTHING ERROR: Not enough values to smooth.")
            return []
        s = sum(vals[:period])
        out = [s / period]
        for v in vals[period:]:
            s = out[-1] * (period - 1) + v
            out.append(s / period)
        return out

    sm_pl = smooth(plus_dm)
    sm_mn = smooth(minus_dm)
    sm_tr = smooth(tr)

    if not sm_pl or not sm_mn or not sm_tr:
        print("ADX SMOOTH ERROR: One or more smoothed lists are empty.")
        return None

    di_plus = [100 * p / t if t != 0 else 0 for p, t in zip(sm_pl, sm_tr)]
    di_minus = [100 * m / t if t != 0 else 0 for m, t in zip(sm_mn, sm_tr)]

    dx = [100 * abs(dp - dm) / (dp + dm) if (dp + dm) != 0 else 0 for dp, dm in zip(di_plus, di_minus)]

    adx_vals = smooth(dx)
    if not adx_vals:
        print("ADX FINAL ERROR: ADX values empty after smoothing.")
        return None

    return adx_vals[-1]
