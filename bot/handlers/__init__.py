"""Handler registration for the bot."""

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.handlers.start import start_handler
from bot.handlers.profile import profile_handler
from bot.handlers.pokemon import pokemon_handler, team_handler, catch_handler
from bot.handlers.spawn import spawn_handler, auto_spawn_handler
from bot.handlers.admin import admin_handler
from bot.handlers.help import help_handler
from bot.handlers.daily import daily_handler
from bot.handlers.shop import shop_handler
from bot.handlers.inline import inline_callback_router


def register_handlers(application: Application) -> None:
    """Register all command and message handlers."""
    
    # Basic commands
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("daily", daily_handler))
    application.add_handler(CommandHandler("shop", shop_handler))
    
    # Profile and stats
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(CommandHandler(["p", "pokemon"], pokemon_handler))
    application.add_handler(CommandHandler("team", team_handler))
    
    # Spawning and catching
    application.add_handler(CommandHandler("spawn", spawn_handler))
    application.add_handler(CommandHandler(["c", "catch"], catch_handler))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_handler))
    
    # Auto-spawn on messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
        auto_spawn_handler
    ))
    
    # Inline keyboard callback handlers
    application.add_handler(CallbackQueryHandler(inline_callback_router))
