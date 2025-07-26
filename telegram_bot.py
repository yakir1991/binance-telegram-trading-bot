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
        "The weights must add up to 1"
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
