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

    async def get_historical_klines(self, symbol, interval, lookback):
        """Return synthetic kline data for the requested period."""
        from datetime import datetime, timedelta
        import random

        # very rough parsing of lookback like "365 days ago UTC"
        try:
            days = int(str(lookback).split()[0])
        except Exception:
            days = 365

        # assume hourly interval regardless of the value passed
        points = days * 24
        now = datetime.utcnow() - timedelta(hours=points)

        klines = []
        base_price = self.prices.get(symbol, 100.0)
        for i in range(points):
            open_time = int((now + timedelta(hours=i)).timestamp() * 1000)
            close_time = int((now + timedelta(hours=i + 1)).timestamp() * 1000)
            open_p = base_price * (1 + random.uniform(-0.01, 0.01))
            close_p = base_price * (1 + random.uniform(-0.01, 0.01))
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
            volume = random.uniform(1, 10)
            klines.append(
                [
                    open_time,
                    str(open_p),
                    str(high_p),
                    str(low_p),
                    str(close_p),
                    str(volume),
                    close_time,
                    "0",
                    0,
                    "0",
                    "0",
                    "0",
                ]
            )
        return klines

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
        # In dummy mode allow selling even if balance is insufficient by
        # permitting negative positions. This avoids errors when a strategy
        # attempts to close a nonexistent holding.
        self.balances.setdefault(base, {"free": 0.0, "locked": 0.0})
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
