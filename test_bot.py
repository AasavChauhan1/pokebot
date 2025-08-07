"""Simple test runner for the bot without databases."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from decouple import config
from telegram.ext import Application, CommandHandler, MessageHandler, filters


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def start_handler(update, context):
    """Simple start handler for testing."""
    await update.message.reply_text(
        "🔥 **Welcome to PokéBot!** 🔥\n\n"
        "✨ This is a test version running without databases.\n"
        "🎮 In the full version, you can catch, battle, and trade Pokémon!\n\n"
        "Commands available in this test:\n"
        "• `/start` - This message\n"
        "• `/test` - Test command\n"
        "• `/help` - Get help\n\n"
        "To run the full version, set up MongoDB and Redis!",
        parse_mode='Markdown'
    )


async def test_handler(update, context):
    """Test handler."""
    await update.message.reply_text(
        "🧪 **Test Command Working!**\n\n"
        "✅ Bot is responding correctly\n"
        "✅ Telegram integration works\n"
        "✅ Message parsing works\n\n"
        "🚀 Ready to set up databases for full functionality!"
    )


async def help_handler(update, context):
    """Help handler."""
    await update.message.reply_text(
        "🔥 **PokéBot Test Version** 🔥\n\n"
        "This is a simplified version for testing the Telegram integration.\n\n"
        "**Setup Instructions for Full Version:**\n"
        "1. Install MongoDB and Redis, OR\n"
        "2. Use Docker: `docker-compose up -d`\n"
        "3. Run: `python main.py`\n\n"
        "**Features in Full Version:**\n"
        "🐾 Pokémon catching and collecting\n"
        "⚔️ Battle system\n"
        "💰 Economy and shop\n"
        "🏆 Leaderboards and achievements\n"
        "🔄 Trading system\n\n"
        "Need help? Check the README.md file!"
    )


async def echo_handler(update, context):
    """Echo handler for testing."""
    text = update.message.text
    await update.message.reply_text(f"🤖 Echo: {text}")


async def main():
    """Main function for test bot."""
    application = None
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Get bot token
        bot_token = config('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN not found in .env file!")
            return
        
        logger.info("🚀 Starting PokéBot Test Version...")
        
        # Create application
        application = Application.builder().token(bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("test", test_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
        
        logger.info("✅ Bot is starting... (Test Mode)")
        logger.info("🔗 Bot token configured successfully")
        logger.info("📱 Ready to receive messages!")
        
        # Start the bot
        await application.run_polling(
            allowed_updates=['message', 'callback_query']
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if application:
            try:
                await application.shutdown()
            except:
                pass


if __name__ == '__main__':
    print("🔥 PokéBot Test Version 🔥")
    print("=" * 40)
    print("This version runs without databases for testing.")
    print("Use /start, /test, and /help commands in Telegram.")
    print("Press Ctrl+C to stop the bot.")
    print("=" * 40)
    
    asyncio.run(main())
