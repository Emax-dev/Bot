# Crypto Price Telegram Bot

A Telegram bot that updates a message with current cryptocurrency prices (BTC, ETH, SOL) in your Telegram channel.

## Setup

1. Create a new bot with [@BotFather](https://t.me/BotFather) on Telegram and get your bot token.

2. Add the bot to your channel:
   - Make the bot an administrator in your channel
   - Give it permission to send messages and edit messages
   - Get your channel ID (you can use @username_to_id_bot to get it)

3. Create a `.env` file in the project directory and add your bot token and channel ID:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the bot:
```bash
python crypto_price_bot.py
```

2. In your private chat with the bot:
   - Send `/start` to initialize the price updates in your channel
   - Use `/interval <minutes>` to change the update frequency
   - Example: `/interval 5` will update the price every 5 minutes

## Features

- Automatically updates Bitcoin, Ethereum, and Solana prices
- Shows last update time
- Easy to set custom update intervals
- Uses CoinGecko API for reliable price data
- Works in Telegram channels

## Note

Make sure the bot has the following permissions in your channel:
- Can send messages
- Can edit messages
- Is an administrator 