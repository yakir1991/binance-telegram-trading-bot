"""
Sentiment-based trading strategy.

This module uses sentiment analysis from news, social media or AI to generate trading signals.
"""

import logging

logger = logging.getLogger(__name__)

async def execute(
    client,
    symbol: str,
    quantity: float,
    sentiment_score: float,
    threshold: float = 0.0,
    bot=None,
    chat_id=None,
):
    """
    Execute sentiment-based strategy.

    Parameters:
        client: Binance client or wrapper for order execution.
        symbol (str): Trading pair.
        quantity (float): Quantity to trade when a signal is triggered.
        sentiment_score (float): Sentiment score in the range [-1, 1], where positive values
            indicate bullish sentiment and negative values indicate bearish sentiment.
        threshold (float): Minimum absolute sentiment value required to trigger a trade.
        bot: Telegram bot instance used to send notifications.
        chat_id: Telegram chat identifier for sending messages.

    If sentiment_score > threshold, a market buy order is placed; if
    sentiment_score < -threshold, a market sell order is placed.
    """
    try:
        logger.info(
            "Executing Sentiment strategy for %s with sentiment %.4f and quantity %f",
            symbol,
            sentiment_score,
            quantity,
        )
        if sentiment_score > threshold:
            if bot and chat_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"Sentiment {sentiment_score:.4f} > {threshold:.4f}. "
                        f"Buying {quantity} of {symbol}."
                    ),
                )
            order = await client.order_market_buy(symbol=symbol, quantity=quantity)
            logger.info("Sentiment buy order: %s", order)
        elif sentiment_score < -threshold:
            if bot and chat_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"Sentiment {sentiment_score:.4f} < -{threshold:.4f}. "
                        f"Selling {quantity} of {symbol}."
                    ),
                )
            order = await client.order_market_sell(symbol=symbol, quantity=quantity)
            logger.info("Sentiment sell order: %s", order)
    except Exception as e:
        logger.exception("Error executing Sentiment strategy: %s", e)
