"""
Simplified bot startup script to avoid event loop issues.
"""

import asyncio
import logging
import sys
from pathlib import Path

from telegram.ext import Application
from config.settings import Settings
from config.database import db
from bot.handlers import register_handlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('pokebot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def start_bot():
    """Start the Pokémon bot with fast auto-spawning."""
    try:
        # Load settings
        settings = Settings()
        logger.info("Starting FAST Pokémon Bot...")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Connect to database
        logger.info("Connecting to PostgreSQL database...")
        await db.connect()
        logger.info("Database connected successfully!")
        
        # Create application
        logger.info("Creating Telegram application...")
        application = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Register handlers
        logger.info("Registering bot handlers...")
        register_handlers(application)
        
        # Initialize application
        logger.info("Initializing application...")
        await application.initialize()
        
        # Start fast auto-spawning system
        logger.info("Starting FAST auto-spawning system...")
        from bot.services.scheduler_service import scheduler_service
        await scheduler_service.start_auto_spawning()
        logger.info("⚡ Fast auto-spawning is ACTIVE! Spawns every 30-60 seconds!")
        
        # Start polling
        logger.info("🚀 FAST Bot is now running! Press Ctrl+C to stop.")
        await application.start()
        await application.updater.start_polling(
            allowed_updates=['message', 'callback_query', 'inline_query']
        )
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Fast bot stopped by user")
    except Exception as e:
        logger.error(f"Fast bot error: {e}")
        raise
    finally:
        # Cleanup
        try:
            # Stop auto-spawning
            from bot.services.scheduler_service import scheduler_service
            await scheduler_service.stop_auto_spawning()
            logger.info("Fast auto-spawning stopped")
            
            if 'application' in locals():
                await application.stop()
                await application.shutdown()
            await db.disconnect()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def main():
    """Main entry point."""
    try:
        # Run the bot
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
