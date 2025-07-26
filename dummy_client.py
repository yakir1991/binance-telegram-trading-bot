import asyncio

class DummyClient:
    """Simple simulated Binance client for offline testing."""

    def __init__(self, start_balance=1000.0, fee_rate=0.001):
        # balances stored as {asset: {'free': float, 'locked': float}}
        self.balances = {"USDT": {"free": float(start_balance), "locked": 0.0}}
        # trade history list
        self.trades = []
        # static prices for a couple of symbols
        self.prices = {"BTCUSDT": 30000.0, "ETHUSDT": 2000.0}
        self.fee_rate = fee_rate

    async def get_account(self):
        return {
            "balances": [
                {"asset": a, "free": str(v["free"]), "locked": str(v["locked"])}
                for a, v in self.balances.items()
            ]
        }

    async def get_my_trades(self, symbol):
        return [t for t in self.trades if t["symbol"] == symbol]

    async def get_avg_price(self, symbol):
        price = self.prices.get(symbol, 0.0)
        return {"price": str(price)}

    async def order_market_buy(self, symbol, quantity):
        price = self.prices.get(symbol, 0.0)
        cost = price * quantity
        fee = cost * self.fee_rate
        if self.balances["USDT"]["free"] < cost + fee:
            raise RuntimeError("Insufficient USDT balance")
        self.balances["USDT"]["free"] -= cost + fee
        base = symbol.replace("USDT", "")
        self.balances.setdefault(base, {"free": 0.0, "locked": 0.0})
        self.balances[base]["free"] += quantity
        self.trades.append({
            "symbol": symbol,
            "qty": str(quantity),
            "price": str(price),
            "isBuyer": True,
        })
        return {"status": "FILLED"}

    async def order_market_sell(self, symbol, quantity):
        price = self.prices.get(symbol, 0.0)
        base = symbol.replace("USDT", "")
        if self.balances.get(base, {"free": 0.0})["free"] < quantity:
            raise RuntimeError("Insufficient balance")
        self.balances[base]["free"] -= quantity
        proceeds = price * quantity
        fee = proceeds * self.fee_rate
        self.balances["USDT"]["free"] += proceeds - fee
        self.trades.append({
            "symbol": symbol,
            "qty": str(quantity),
            "price": str(price),
            "isBuyer": False,
        })
        return {"status": "FILLED"}

    async def close_connection(self):
        # Nothing to close in the dummy client
        pass
