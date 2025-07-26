import os
import env_loader
from binance import AsyncClient
from dummy_client import DummyClient

async def get_binance_client():
    """
    Create and return a client for Binance.

    By default a local simulation is used when the environment variable
    ``DUMMY_ACCOUNT`` is set to a truthy value. The simulated account
    starts with 1000 USDT and charges a 0.1%% fee on each trade.
    Otherwise a real ``AsyncClient`` is returned using the provided
    API credentials. Testnet mode is disabled.
    """
    if os.getenv("DUMMY_ACCOUNT", "false").lower() in ("1", "true", "yes"):
        return DummyClient()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError(
            "BINANCE_API_KEY or BINANCE_API_SECRET environment variables are not set"
        )

    client = await AsyncClient.create(api_key, api_secret, testnet=False)
    return client
