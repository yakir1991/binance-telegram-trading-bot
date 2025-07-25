import os
from binance import AsyncClient

async def get_binance_client():
    """
    Create and return an AsyncClient for Binance.

    Uses API credentials from environment variables BINANCE_API_KEY and BINANCE_API_SECRET.
    If the environment variable TESTNET is set to a truthy value (e.g. "true", "1", "yes"),
    the client will connect to the Binance Spot testnet for demo trading; otherwise,
    it connects to the live trading environment.
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("BINANCE_API_KEY or BINANCE_API_SECRET environment variables are not set")

    testnet = os.getenv("TESTNET", "false").lower() in ("1", "true", "yes")
    client = await AsyncClient.create(api_key, api_secret, testnet=testnet)
    return client
