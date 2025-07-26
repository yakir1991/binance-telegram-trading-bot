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

## Risk Level

You can adjust how aggressively the bot trades by setting a risk level between `0.0` and `1.0`.
The risk level acts as a multiplier on all trade sizes. Use `/risk` to see the
current level and `/setrisk <level>` to change it. For example, to trade at half
your usual size:

```
/setrisk 0.5
```

Setting the risk level to `0` effectively pauses trading, while `1` leaves trade
sizes unchanged.

## Running the Bot

Install the required packages from `requirements.txt` and then start the bot:

```
python telegram_bot.py
```

## Portfolio Command

Use `/portfolio` in Telegram to view a detailed summary of your Binance account.
The bot reports the balance of each asset, the average purchase price based on
your trade history, the current market price and the resulting profit or loss.
