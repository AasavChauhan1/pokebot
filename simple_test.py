"""Simple bot test without complex async handling."""

import logging
from telegram.ext import Application, CommandHandler
from decouple import config


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update, context):
    """Start command handler."""
    await update.message.reply_text(
        "🔥 **PokéBot is WORKING!** 🔥\n\n"
        "✅ Telegram integration successful!\n"
        "✅ Bot token is valid!\n"
        "✅ Commands are working!\n\n"
        "🚀 Ready to set up the full bot with databases!\n\n"
        "Try: /test, /help",
        parse_mode='Markdown'
    )


async def test(update, context):
    """Test command."""
    await update.message.reply_text(
        "🧪 **Test Successful!**\n\n"
        "All systems go! 🚀"
    )


async def help_cmd(update, context):
    """Help command."""
    await update.message.reply_text(
        "🔥 **PokéBot Test Commands:**\n\n"
        "• `/start` - Welcome message\n"
        "• `/test` - Test functionality\n"
        "• `/help` - This help message\n\n"
        "**Next Steps:**\n"
        "1. Set up MongoDB and Redis\n"
        "2. Run the full bot with `python main.py`\n"
        "3. Start catching Pokémon! 🐾"
    )


def main():
    """Main function."""
    print("🔥 PokéBot Quick Test 🔥")
    print("=" * 30)
    
    try:
        bot_token = config('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN not found!")
            return
        
        print("✅ Bot token found")
        print("🚀 Starting bot...")
        
        app = Application.builder().token(bot_token).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("test", test))
        app.add_handler(CommandHandler("help", help_cmd))
        
        print("📱 Bot is running! Send /start in Telegram")
        print("🛑 Press Ctrl+C to stop")
        
        app.run_polling()
        
    except KeyboardInterrupt:
        print("\n✅ Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
