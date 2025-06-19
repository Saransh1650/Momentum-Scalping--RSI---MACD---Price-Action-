def fmt(val, precision=2):
    return f"{val:.{precision}f}" if val is not None else "--"
