import logging
import pandas as pd
from binance import AsyncClient

import binance_client

logger = logging.getLogger(__name__)


async def fetch_historical_data(symbol: str, interval: str, lookback: str):
    """Download historical klines from Binance and return as DataFrame."""
    client = await binance_client.get_binance_client()
    try:
        klines = await client.get_historical_klines(symbol, interval, lookback)
    finally:
        await client.close_connection()

    df = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


async def calculate_recommended_weights(
    symbol: str,
    interval: str = AsyncClient.KLINE_INTERVAL_1HOUR,
    lookback: str = "30 days ago UTC",
) -> dict:
    """Return recommended strategy weights based on simple performance metrics."""
    df = await fetch_historical_data(symbol, interval, lookback)
    returns = df["close"].pct_change().dropna()
    momentum = returns.mean()
    volatility = returns.std()

    metrics = {
        "dca": max(momentum, 0.0) + 1e-9,
        "grid": volatility + 1e-9,
        "scalping": volatility / 2 + 1e-9,
        "trend": abs(momentum) + 1e-9,
        "sentiment": 1e-9,  # placeholder metric
    }
    total = sum(metrics.values())
    weights = {k: v / total for k, v in metrics.items()}
    logger.info("Recommended weights calculated: %s", weights)
    return weights


async def calculate_recommended_weights_with_progress(
    symbol: str,
    interval: str = AsyncClient.KLINE_INTERVAL_1HOUR,
    lookback: str = "30 days ago UTC",
    bot=None,
    chat_id=None,
) -> dict:
    """Calculate recommended weights and optionally send progress updates."""

    if bot and chat_id:
        await bot.send_message(chat_id=chat_id, text="Fetching historical data...")

    df = await fetch_historical_data(symbol, interval, lookback)

    if bot and chat_id:
        await bot.send_message(chat_id=chat_id, text="Calculating weight metrics...")

    returns = df["close"].pct_change().dropna()
    momentum = returns.mean()
    volatility = returns.std()

    metrics = {
        "dca": max(momentum, 0.0) + 1e-9,
        "grid": volatility + 1e-9,
        "scalping": volatility / 2 + 1e-9,
        "trend": abs(momentum) + 1e-9,
        "sentiment": 1e-9,
    }

    total = sum(metrics.values())
    weights = {k: v / total for k, v in metrics.items()}

    logger.info("Recommended weights calculated: %s", weights)

    if bot and chat_id:
        await bot.send_message(chat_id=chat_id, text="Training complete.")

    return weights
