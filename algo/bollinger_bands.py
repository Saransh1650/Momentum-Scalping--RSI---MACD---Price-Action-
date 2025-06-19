import numpy as np

def bollinger_bands(close_prices, period=20, std_dev=2):
    if len(close_prices) < period:
        print("bollinger plate values are null")
        return None, None, None

    try:
        slice_ = np.array(close_prices[-period:], dtype=float)
        mid = slice_.mean()
        sd = slice_.std()
        return mid, mid + std_dev * sd, mid - std_dev * sd
    except (ValueError, TypeError):
        return None, None, None
