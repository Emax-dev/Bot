import os
import logging
from datetime import datetime
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Get bot token and channel ID from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

if not TOKEN:
    raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")
if not CHANNEL_ID:
    raise ValueError("Please set the TELEGRAM_CHANNEL_ID environment variable")

logger.debug(f"Bot token: {TOKEN[:5]}...")  # Log first 5 chars of token
logger.debug(f"Channel ID: {CHANNEL_ID}")

# Store the message ID that will be updated
message_id = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initialize the price updates in the channel."""
    global message_id
    logger.debug("Received /start command")
    
    try:
        # First, try to get chat info to verify channel access
        logger.debug(f"Attempting to get chat info for {CHANNEL_ID}")
        chat = await context.bot.get_chat(chat_id=CHANNEL_ID)
        logger.debug(f"Chat info: {chat}")
        
        # Send initial message to the channel
        logger.debug(f"Sending initial message to channel {CHANNEL_ID}")
        message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="Starting price updates..."
        )
        message_id = message.message_id
        logger.debug(f"Message sent with ID: {message_id}")
        
        # Set default interval to 5 minutes
        job = context.job_queue.run_repeating(update_price, interval=300, first=0)
        context.chat_data['job'] = job
        logger.debug("Scheduled price updates every 5 minutes")
        
        # Immediately update the price
        logger.debug("Performing initial price update")
        await update_price(context)
        logger.debug("Initial price update completed")
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        error_message = (
            "Error starting the bot. Please check:\n"
            "1. The bot is an admin in the channel\n"
            "2. The bot has permission to send and edit messages\n"
            "3. The channel ID is correct\n"
            f"Error details: {str(e)}\n"
            f"Channel ID used: {CHANNEL_ID}"
        )
        await update.message.reply_text(error_message)

async def get_exchange_rate() -> float:
    """Get current USD to IRR exchange rate."""
    try:
        # Using CoinGecko API for exchange rates
        response = requests.get('https://api.coingecko.com/api/v3/exchange_rates')
        if response.status_code == 200:
            data = response.json()
            # Get USD rate and convert to IRR (approximate rate)
            usd_rate = data['rates']['usd']['value']
            # Approximate conversion (you can adjust this multiplier)
            irr_rate = usd_rate * 50000
            return irr_rate
        else:
            logger.error(f"Failed to get exchange rate: {response.text}")
            return 50000  # Fallback rate if API fails
    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}")
        return 50000  # Fallback rate if API fails

async def get_usdt_irr_rate() -> float:
    """Get current USDT to IRR rate from Nobitex."""
    try:
        # Using Nobitex API for USDT/IRR rate
        response = requests.get('https://api.nobitex.ir/v2/orderbook/USDTIRT')
        if response.status_code == 200:
            data = response.json()
            # Get the average of best bid and ask
            best_bid = float(data['bids'][0][0])  # Highest buy price
            best_ask = float(data['asks'][0][0])  # Lowest sell price
            average_rate = (best_bid + best_ask) / 2
            return average_rate
        else:
            logger.error(f"Failed to get USDT rate: {response.text}")
            return 50000  # Fallback rate if API fails
    except Exception as e:
        logger.error(f"Error getting USDT rate: {e}")
        return 50000  # Fallback rate if API fails

async def update_price(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update the message with current crypto prices."""
    if not message_id:
        logger.debug("No message ID available for update")
        return

    try:
        logger.debug("Fetching crypto prices from CoinGecko API")
        # Fetch prices from CoinGecko API
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,tether&vs_currencies=usd')
        logger.debug(f"API Response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"API Error: {response.text}")
            return
            
        data = response.json()
        logger.debug("Successfully parsed API response")
        
        btc_price = data['bitcoin']['usd']
        eth_price = data['ethereum']['usd']
        sol_price = data['solana']['usd']
        usdt_usd = data['tether']['usd']
        
        # Get current USDT to IRR rate
        usdt_irr_rate = await get_usdt_irr_rate()
        
        # Get current time in Iran's timezone
        tehran_tz = pytz.timezone('Asia/Tehran')
        current_time = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")
        
        message_text = (
            f"💰 Bitcoin (BTC): ${btc_price:,.2f}\n"
            f"💎 Ethereum (ETH): ${eth_price:,.2f}\n"
            f"✨ Solana (SOL): ${sol_price:,.2f}\n"
            f"💵 Tether (USDT): {usdt_irr_rate:,.0f} ریال"
        )
        
        logger.debug(f"Updating message with new prices")
        await context.bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=message_id,
            text=message_text
        )
        logger.debug("Message updated successfully")
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        logger.error(f"Error details: {str(e)}")

def main() -> None:
    """Start the bot."""
    logger.debug("Starting bot...")
    try:
        # Create the Application
        application = Application.builder().token(TOKEN).build()

        # Add command handler
        application.add_handler(CommandHandler("start", start))

        # Start the Bot
        logger.debug("Bot is running and waiting for commands...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == '__main__':
    main() 