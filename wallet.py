from decimal import Decimal

class Wallet:
    def __init__(self, initial_balance=1000.0):
        self.usdt = Decimal(initial_balance)
        self.crypto = Decimal('0.0')
        self.last_price = Decimal('0.0')

    def buy(self, price, amount_pct=1.0):
        price = Decimal(str(price))
        amount_pct = Decimal(str(amount_pct))
        amount_to_spend = self.usdt * amount_pct
        if amount_to_spend <= 0:
            return
        crypto_bought = amount_to_spend / price
        self.usdt -= amount_to_spend
        self.crypto += crypto_bought
        self.last_price = price
        print(f"Bought {crypto_bought:.6f} units at ${price:.2f}, USDT left: {self.usdt:.2f}")

    def sell(self, price, amount_pct=1.0):
        price = Decimal(str(price))
        amount_pct = Decimal(str(amount_pct))
        amount_to_sell = self.crypto * amount_pct
        if amount_to_sell <= 0:
            return
        proceeds = amount_to_sell * price
        self.crypto -= amount_to_sell
        self.usdt += proceeds
        self.last_price = price
        print(f"Sold {amount_to_sell:.6f} units at ${price:.2f}, USDT now: {self.usdt:.2f}")

    def summary(self, current_price):
        current_price = Decimal(str(current_price))
        total_value = self.usdt + self.crypto * current_price
        print(f"Total wallet value: ${total_value:.2f} | USDT: {self.usdt:.2f} | Crypto: {self.crypto:.6f}")
