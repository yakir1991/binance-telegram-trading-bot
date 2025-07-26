import os
import env_loader
import asyncio
import logging

from trading_tasks import dca_loop, grid_loop, scalping_loop, trend_loop, sentiment_loop
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    await update.message.reply_text(
        "Hello! I'm your Binance trading bot.\n"
        "I run various trading strategies and report status on Telegram.\n"
        "Use the /help command to see all available commands."
    )

async def status_command(update, context):
    await update.message.reply_text(
        "The strategies are running in the background. Check the logs for more information."
    )

async def help_command(update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - initiate conversation with the bot\n"
        "/status - check the current strategy status\n"
        "/help - show this command list"
    )

async def telegram_bot():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. Please set your Telegram bot token."
        )

    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Starting Telegram bot polling")
    await asyncio.to_thread(application.run_polling)

async def trading_tasks_runner():
    tasks = [
        asyncio.create_task(dca_loop()),
        asyncio.create_task(grid_loop()),
        asyncio.create_task(scalping_loop()),
        asyncio.create_task(trend_loop()),
        asyncio.create_task(sentiment_loop()),
    ]
    await asyncio.gather(*tasks)

async def main():
    await asyncio.gather(
        trading_tasks_runner(),
        telegram_bot(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
