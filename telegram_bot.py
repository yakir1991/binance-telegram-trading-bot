import os
import env_loader
import asyncio
import logging

from trading_tasks import (
    dca_loop,
    grid_loop,
    scalping_loop,
    trend_loop,
    sentiment_loop,
    CONFIG,
)
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import binance_client

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update, context):
    await update.message.reply_text(
        "Hello! I'm your Binance trading bot.\n"
        "I run various trading strategies and update you on Telegram.\n"
        "Use the /help command to see all available commands."
    )


async def status_command(update, context):
    await update.message.reply_text(
        "The strategies are running in the background. Check the logs for more details."
    )


async def help_command(update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/start – start chatting with the bot\n"
        "/status – check the current status of the strategies\n"
        "/help – display this command list\n"
        "/weights – show current strategy weights\n"
        "/setweights – set new strategy weights\n"
        "Usage: /setweights <dca> <grid> <scalping> <trend> <sentiment>\n"
        "The weights must add up to 1\n"
        "/risk – show current risk level\n"
        "/setrisk – set a new risk level (0.0-1.0)\n"
        "/portfolio – show detailed account portfolio"
    )


async def weights_command(update, context):
    weights = CONFIG.get("weights", {})
    message = "Current strategy weights:\n"
    for name, value in weights.items():
        message += f"{name}: {value:.2f}\n"
    await update.message.reply_text(message)


async def setweights_command(update, context):
    if len(context.args) != 5:
        await update.message.reply_text(
            "Usage: /setweights <dca> <grid> <scalping> <trend> <sentiment>"
        )
        return
    try:
        dca_w, grid_w, scalping_w, trend_w, sentiment_w = map(float, context.args)
    except ValueError:
        await update.message.reply_text("All weights must be numbers")
        return
    total = dca_w + grid_w + scalping_w + trend_w + sentiment_w
    if abs(total - 1.0) > 1e-6:
        await update.message.reply_text("Total weight must equal 1")
        return

    CONFIG["weights"].update(
        {
            "dca": dca_w,
            "grid": grid_w,
            "scalping": scalping_w,
            "trend": trend_w,
            "sentiment": sentiment_w,
        }
    )
    await update.message.reply_text("Weights updated")


async def risk_command(update, context):
    risk = CONFIG.get("risk_level", 1.0)
    await update.message.reply_text(f"Current risk level: {risk:.2f}")


async def setrisk_command(update, context):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setrisk <level> (0.0-1.0)")
        return
    try:
        level = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Risk level must be a number")
        return
    if level < 0 or level > 1:
        await update.message.reply_text("Risk level must be between 0.0 and 1.0")
        return
    CONFIG["risk_level"] = level
    await update.message.reply_text(f"Risk level set to {level:.2f}")


async def portfolio_command(update, context):
    """Display account portfolio with purchase price and PnL."""
    try:
        client = await binance_client.get_binance_client()
    except Exception as e:
        await update.message.reply_text(f"Error connecting to Binance: {e}")
        return

    try:
        account = await client.get_account()
    except Exception as e:
        await update.message.reply_text(f"Failed to fetch account: {e}")
        await client.close_connection()
        return

    message = "Your portfolio:\n"
    for balance in account.get("balances", []):
        free = float(balance.get("free", 0))
        locked = float(balance.get("locked", 0))
        total = free + locked
        if total == 0:
            continue
        asset = balance.get("asset")

        symbol = f"{asset}USDT"
        qty = 0.0
        cost = 0.0
        try:
            trades = await client.get_my_trades(symbol=symbol)
        except Exception:
            trades = []

        for t in trades:
            q = float(t["qty"])
            price = float(t["price"])
            if t["isBuyer"]:
                qty += q
                cost += price * q
            else:
                qty -= q
                cost -= price * q

        avg_price = cost / qty if qty != 0 else 0.0
        try:
            ticker = await client.get_avg_price(symbol=symbol)
            current_price = float(ticker["price"])
        except Exception:
            current_price = 0.0
        pnl = (current_price - avg_price) * qty if qty != 0 else 0.0

        message += (
            f"{asset}: balance={total:.4f}, avg_buy={avg_price:.4f}, "
            f"current={current_price:.4f}, PnL={pnl:.4f}\n"
        )

    await client.close_connection()
    await update.message.reply_text(message)


def main() -> None:
    """Start the Telegram bot and trading tasks."""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. Please set your Telegram bot token."
        )

    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weights", weights_command))
    application.add_handler(CommandHandler("setweights", setweights_command))
    application.add_handler(CommandHandler("risk", risk_command))
    application.add_handler(CommandHandler("setrisk", setrisk_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))

    loop = asyncio.get_event_loop()
    loop.create_task(dca_loop())
    loop.create_task(grid_loop())
    loop.create_task(scalping_loop())
    loop.create_task(trend_loop())
    loop.create_task(sentiment_loop())

    logger.info("Starting Telegram bot polling")
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
