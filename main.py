"""
Pokémon Telegram Bot
A feature-rich bot with spawning, battles, trading, and economy systems.
"""

import asyncio
import logging
import sys
from pathlib import Path

from decouple import config
from telegram.ext import Application

from bot import create_bot
from config.settings import Settings


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = config('LOG_LEVEL', default='INFO')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, log_level.upper()),
        handlers=[
            logging.FileHandler('pokebot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def main() -> None:
    """Main function to start the bot."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load settings
        settings = Settings()
        
        logger.info("Starting Pokémon Telegram Bot...")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Create and start the bot
        application = await create_bot(settings)
        
        # Start the bot
        logger.info("Bot is starting...")
        await application.run_polling(
            allowed_updates=['message', 'callback_query', 'inline_query']
        )
        
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
