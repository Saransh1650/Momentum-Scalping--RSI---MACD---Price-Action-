def get_order_book_pressure(bids, asks, top_n=5):
    if not bids or not asks:
        print("[WARNING] Empty order book, skipping this tick.")
        return 0  
    
    def safe_volume(entry):
        try:
            return float(entry[1])
        except (IndexError, ValueError, TypeError):
            return 0

    sum_bid_vol = sum(safe_volume(bid) for bid in bids[:top_n])
    sum_ask_vol = sum(safe_volume(ask) for ask in asks[:top_n])
    total_vol = sum_bid_vol + sum_ask_vol

    if total_vol == 0:
        print("total volume is null")
        return 0

    pressure = (sum_bid_vol - sum_ask_vol) / total_vol
    print(f"calculated pressure: {pressure}")
    return pressure
