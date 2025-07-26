# binance-telegram-trading-bot
Trading bot for Binance integrated with Telegram, focusing on informative and interactive messages and detailed logging.

## Setup

1. Copy `.env.example` to `.env`.
2. Edit `.env` and provide your Binance API keys and Telegram bot token.

The bot loads this file automatically on startup so your environment variables are available.

## Strategy Weights

You can control how much capital each strategy uses by setting weights from Telegram. The weights of all strategies must sum to `1`.

Use `/weights` to view the current weights and `/setweights <dca> <grid> <scalping> <trend> <sentiment>` to update them. For example:

```
/setweights 0.2 0.2 0.2 0.2 0.2
```

## Running the Bot

Install the required packages from `requirements.txt` and then start the bot:

```
python telegram_bot.py
```
