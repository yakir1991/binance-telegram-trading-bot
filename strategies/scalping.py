"""
Scalping (day trading) strategy.

This strategy aims to capture small price movements quickly and exit positions within a short time frame.
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
    Execute Scalping strategy.

    Parameters:
        client: Binance client for order execution.
        symbol (str): Trading pair.
        quantity (float): Quantity to trade per signal.
        indicators (dict): Parameters controlling the moving average periods.
        weight (float): Weight of this strategy when executed.

    The strategy calculates simple moving averages on hourly closes and places
    market orders when the fast average crosses the slow one.
    """
    try:
        message = (
            "Executing Scalping strategy for %s with quantity %f and indicators: %s (weight %.2f)"
            % (symbol, quantity, indicators, weight)
        )
        logger.info(message)
        if bot and chat_id:
            await bot.send_message(chat_id=chat_id, text=message)

        short_period = int(indicators.get("ema_fast", 7))
        long_period = int(indicators.get("ema_slow", 25))
        lookback = int(indicators.get("lookback", long_period + 5))

        klines = await client.get_historical_klines(
            symbol, interval="1h", lookback=f"{lookback} hours ago UTC"
        )
        closes = [float(k[4]) for k in klines]
        if len(closes) < long_period:
            logger.warning("Not enough data for scalping")
            return

        short_ma = sum(closes[-short_period:]) / short_period
        long_ma = sum(closes[-long_period:]) / long_period

        if short_ma > long_ma:
            trade_msg = (
                f"Scalping signal BUY {quantity} {symbol}: short_ma {short_ma:.4f} > long_ma {long_ma:.4f}"
            )
            if bot and chat_id:
                await bot.send_message(chat_id=chat_id, text=trade_msg)
            order = await client.order_market_buy(symbol=symbol, quantity=quantity)
            logger.info("Scalping buy order: %s", order)
        elif short_ma < long_ma:
            trade_msg = (
                f"Scalping signal SELL {quantity} {symbol}: short_ma {short_ma:.4f} < long_ma {long_ma:.4f}"
            )
            if bot and chat_id:
                await bot.send_message(chat_id=chat_id, text=trade_msg)
            order = await client.order_market_sell(symbol=symbol, quantity=quantity)
            logger.info("Scalping sell order: %s", order)
    except Exception as e:
        logger.exception("Error executing Scalping strategy: %s", e)
