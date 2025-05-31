class Wallet:
    def __init__(self):
        self.crypto = 0
        self.fiat = 2500  # Example starting capital

    def buy(self, price, amount_pct=1.0):
        amount = (self.fiat * amount_pct) / price
        self.crypto += amount
        self.fiat -= amount * price
        print(f"[BUY] Bought {amount:.6f} crypto at {price:.2f}")

    def sell(self, price, amount_pct=1.0):
        amount = self.crypto * amount_pct
        self.crypto -= amount
        self.fiat += amount * price
        print(f"[SELL] Sold {amount:.6f} crypto at {price:.2f}")