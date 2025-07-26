"""
Trend following strategy.

This strategy seeks to enter trades in the direction of the prevailing trend
based on indicators such as moving averages or momentum.
"""

import logging

logger = logging.getLogger(__name__)

async def execute(
    client,
    symbol: str,
    quantity: float,
    indicators: dict,
    weight: float,
    bot=None,
    chat_id=None,
):
    """
    Execute Trend Following strategy.

    Parameters:
        client: Binance client or wrapper used for order execution.
        symbol (str): Trading pair.
        quantity (float): Quantity to trade.
        indicators (dict): Precomputed trend indicators (e.g., moving average crossover, ADX).
        weight (float): Weight of this strategy when executed.

    Uses trend signals to decide long or short positions.
    """
    try:
        message = (
            "Executing Trend strategy for %s with quantity %f and indicators: %s (weight %.2f)"
            % (symbol, quantity, indicators, weight)
        )
        logger.info(message)
        if bot and chat_id:
            await bot.send_message(chat_id=chat_id, text=message)
        # Example logic:
        # if indicators.get("trend_signal") > 0:
        #     # Positive trend: go long
        #     order = await client.order_market_buy(symbol=symbol, quantity=quantity)
        #     logger.info("Trend-following buy order: %s", order)
        # elif indicators.get("trend_signal") < 0:
        #     # Negative trend: go short/sell
        #     order = await client.order_market_sell(symbol=symbol, quantity=quantity)
        #     logger.info("Trend-following sell order: %s", order)
    except Exception as e:
        logger.exception("Error executing Trend Following strategy: %s", e)
