"""Main bot module initialization."""

import logging
from telegram.ext import Application

from config.database import db
from config.settings import Settings
from bot.handlers import register_handlers

logger = logging.getLogger(__name__)


async def create_bot(settings: Settings) -> Application:
    """Create and configure the Telegram bot application."""
    
    # Create application
    application = Application.builder().token(settings.BOT_TOKEN).build()
    
    # Connect to databases
    await db.connect()
    # Indexes are created automatically with SQLAlchemy tables
    
    # Register handlers
    register_handlers(application)
    
    logger.info("Bot created and configured successfully")
    return application
