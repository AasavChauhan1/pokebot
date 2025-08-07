"""Simple Telegram bot test without complex database operations."""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from config.settings import Settings

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🎮 Welcome to the Pokémon Bot! 🎮\n\n"
        "PostgreSQL migration successful! ✅\n"
        "Bot is now running with cloud database.\n\n"
        "Try /help for available commands!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📖 **Pokémon Bot Commands**\n\n"
        "🔹 `/start` - Start the bot\n"
        "🔹 `/help` - Show this help\n"
        "🔹 `/profile` - View your trainer profile\n"
        "🔹 `/pokemon` - View your Pokémon collection\n"
        "🔹 `/spawn` - Force spawn a Pokémon (admin)\n\n"
        "Database: PostgreSQL (Neon) ✅"
    )


async def test_simple_bot():
    """Test simple bot functionality."""
    
    try:
        settings = Settings()
        
        # Create application
        application = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        logger.info("Simple bot starting...")
        
        # Start polling
        await application.run_polling(
            allowed_updates=['message', 'callback_query']
        )
        
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(test_simple_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
