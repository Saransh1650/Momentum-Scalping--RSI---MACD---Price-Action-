class Wallet:
    def __init__(self, initial_balance=1000.0):
        self.usdt = initial_balance
        self.crypto = 0.0
        self.last_price = 0.0

    def buy(self, price, amount_pct=1.0):
        amount_to_spend = self.usdt * amount_pct
        crypto_bought = amount_to_spend / price
        self.usdt -= amount_to_spend
        self.crypto += crypto_bought
        self.last_price = price
        print(f"Bought {crypto_bought:.6f} units at ${price:.2f}, USDT left: {self.usdt:.2f}")

    def sell(self, price, amount_pct=1.0):
        amount_to_sell = self.crypto * amount_pct
        proceeds = amount_to_sell * price
        self.crypto -= amount_to_sell
        self.usdt += proceeds
        self.last_price = price
        print(f"Sold {amount_to_sell:.6f} units at ${price:.2f}, USDT now: {self.usdt:.2f}")

    def summary(self, current_price):
        total_value = self.usdt + self.crypto * current_price
        print(f"Total wallet value: ${total_value:.2f} | USDT: {self.usdt:.2f} | Crypto: {self.crypto:.6f}")
