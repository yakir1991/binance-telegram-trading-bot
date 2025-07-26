import asyncio
import logging
import os
import logger_config
from data_training import calculate_recommended_weights

from strategies import dca, grid, scalping, trend_following, sentiment

# Configure module logger
logger = logging.getLogger(__name__)

# Telegram integration
TELEGRAM_BOT = None
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Bot configuration
CONFIG = {
    "symbols": ["BTCUSDT"],
    "dca_amount": 10.0,
    "dca_interval_minutes": 60,
    "grid": {
        "lower": 30000.0,
        "upper": 35000.0,
        "levels": 10,
    },
    "grid_interval_minutes": 5,
    "scalping_interval_seconds": 60,
    "trend_interval_minutes": 5,
    "sentiment_interval_minutes": 10,
    "weights": {
        "dca": 0.2,
        "grid": 0.2,
        "scalping": 0.2,
        "trend": 0.2,
        "sentiment": 0.2,
    },
    "risk_level": 1.0,
}


async def dca_loop():
    """
    Execute dollar-cost averaging trades at regular intervals.
    """
    while True:
        symbol = CONFIG["symbols"][0]
        weight = CONFIG["weights"]["dca"]
        amount = CONFIG["dca_amount"] * weight * CONFIG.get("risk_level", 1.0)
        interval = CONFIG["dca_interval_minutes"]
        # call the DCA strategy implementation
        await dca.execute(
            client=None,
            symbol=symbol,
            amount=amount,
            interval_minutes=interval,
            weight=weight,
        )
        # wait until the next DCA trade
        await asyncio.sleep(interval * 60)


async def grid_loop():
    """
    Maintain a grid of limit orders between configured lower and upper bounds.
    """
    while True:
        symbol = CONFIG["symbols"][0]
        lower = CONFIG["grid"]["lower"]
        upper = CONFIG["grid"]["upper"]
        levels = CONFIG["grid"]["levels"]
        weight = CONFIG["weights"]["grid"]
        amount = CONFIG["dca_amount"] * weight * CONFIG.get("risk_level", 1.0)
        # call the grid strategy implementation
        await grid.execute(
            client=None,
            symbol=symbol,
            lower_price=lower,
            upper_price=upper,
            grids=levels,
            quantity=amount,
            weight=weight,
        )
        await asyncio.sleep(CONFIG["grid_interval_minutes"] * 60)


async def scalping_loop():
    """
    Run a high-frequency scalping strategy using short-term indicators.
    """
    while True:
        symbol = CONFIG["symbols"][0]
        weight = CONFIG["weights"]["scalping"]
        quantity = CONFIG["dca_amount"] * weight * CONFIG.get("risk_level", 1.0)
        indicators = {"rsi_period": 14, "ema_fast": 7, "ema_slow": 25}
        # call the scalping strategy implementation
        await scalping.execute(
            client=None,
            symbol=symbol,
            quantity=quantity,
            indicators=indicators,
            weight=weight,
            bot=TELEGRAM_BOT,
            chat_id=TELEGRAM_CHAT_ID,
        )
        await asyncio.sleep(CONFIG["scalping_interval_seconds"])


async def trend_loop():
    """
    Run a trend-following strategy using momentum indicators.
    """
    while True:
        symbol = CONFIG["symbols"][0]
        weight = CONFIG["weights"]["trend"]
        quantity = CONFIG["dca_amount"] * weight * CONFIG.get("risk_level", 1.0)

        # call the trend following strategy implementation
        indicators = {"lookback": 100}
        await trend_following.execute(
            client=None,
            symbol=symbol,
            quantity=quantity,
            indicators=indicators,
            weight=weight,
            bot=TELEGRAM_BOT,
            chat_id=TELEGRAM_CHAT_ID,
        )
        await asyncio.sleep(CONFIG["trend_interval_minutes"] * 60)


async def sentiment_loop():
    """
    Run a sentiment-based strategy that reacts to news or social sentiment.
    """
    while True:
        symbol = CONFIG["symbols"][0]
        weight = CONFIG["weights"]["sentiment"]
        quantity = CONFIG["dca_amount"] * weight * CONFIG.get("risk_level", 1.0)
        sentiment_score = (
            0.0  # placeholder sentiment score; integrate actual sentiment analysis here
        )
        # call the sentiment strategy implementation
        await sentiment.execute(
            client=None,
            symbol=symbol,
            sentiment_score=sentiment_score,
            quantity=quantity,
            weight=weight,
            bot=TELEGRAM_BOT,
            chat_id=TELEGRAM_CHAT_ID,
        )
        await asyncio.sleep(CONFIG["sentiment_interval_minutes"] * 60)


async def weight_training_loop():
    """Periodically recalculate strategy weights from historical data."""
    while True:
        symbol = CONFIG["symbols"][0]
        try:
            weights = await calculate_recommended_weights(symbol)
            CONFIG["weights"].update(weights)
            logger.info("Automatically updated weights: %s", weights)
        except Exception as e:
            logger.exception("Failed to update weights: %s", e)
        await asyncio.sleep(24 * 60 * 60)


async def main():
    """
    Entry point for running all strategy loops concurrently.
    """
    tasks = [
        asyncio.create_task(dca_loop()),
        asyncio.create_task(grid_loop()),
        asyncio.create_task(scalping_loop()),
        asyncio.create_task(trend_loop()),
        asyncio.create_task(sentiment_loop()),
        asyncio.create_task(weight_training_loop()),
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
