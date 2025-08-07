"""Inline keyboard callback handlers."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.fast_spawn_service import fast_spawn_service
from bot.utils.helpers import format_pokemon_name, get_rarity_emoji

logger = logging.getLogger(__name__)


async def catch_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle catch button clicks."""
    query = update.callback_query
    user = query.from_user
    
    try:
        # Extract spawn_id from callback data
        if not query.data.startswith("catch_"):
            await query.answer("❌ Invalid action!")
            return
        
        spawn_id = query.data.split("catch_")[1]
        
        # Get spawn details
        spawn = await fast_spawn_service.get_spawn_by_id(spawn_id)
        if not spawn:
            await query.answer("💨 This Pokémon has disappeared!", show_alert=True)
            
            # Update message to show expired
            try:
                await query.edit_message_caption(
                    caption="💨 **This Pokémon has disappeared!**\n\n⏰ Spawns expire after 10 minutes.",
                    parse_mode='Markdown'
                )
            except:
                pass
            return
        
        # Check if already caught
        if spawn.get('is_caught'):
            await query.answer("🎯 This Pokémon was already caught by someone else!", show_alert=True)
            return
        
        # Attempt catch
        success, message = await fast_spawn_service.catch_spawn(spawn_id, user.id)
        
        if success:
            # Success! Update message to show caught
            rarity_emoji = "✨" if spawn['is_shiny'] else get_rarity_emoji(spawn['rarity'])
            name = f"✨ {spawn['species'].title()}" if spawn['is_shiny'] else spawn['species'].title()
            
            caught_message = f"🎉 **POKÉMON CAPTURED!**\n\n"
            caught_message += f"{rarity_emoji} **{name}** (Level {spawn['level']})\n"
            
            if spawn['is_shiny']:
                caught_message += "\n✨ **RARE SHINY CAPTURED!** ✨\n"
            
            caught_message += f"\n👤 **Caught by:** {user.first_name}\n"
            caught_message += f"💬 {message}\n"
            caught_message += f"\n📚 Use `/pokemon` to view collection"
            
            # Create disabled button
            keyboard = [[
                InlineKeyboardButton("✅ Caught!", callback_data="already_caught")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message
            try:
                await query.edit_message_caption(
                    caption=caught_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except:
                # Fallback for text messages
                await query.edit_message_text(
                    text=caught_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
            # Send success notification
            await query.answer("🎉 Pokémon captured successfully!", show_alert=True)
            
        else:
            # Failed catch - but don't update message, let others try
            await query.answer(f"💨 {message} Try again!", show_alert=True)
            
    except Exception as e:
        logger.error(f"Catch button handler error: {e}")
        await query.answer("❌ Catch error! Try again!", show_alert=True)


async def already_caught_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle clicks on already caught Pokemon."""
    query = update.callback_query
    await query.answer("🎯 This Pokémon was already caught!", show_alert=True)


async def shop_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shop-related callbacks."""
    query = update.callback_query
    
    try:
        # Import here to avoid circular imports
        from bot.handlers.shop import shop_category_handler, shop_buy_handler, shop_main_handler
        
        if query.data.startswith("shop_category_"):
            await shop_category_handler(query.data, update, context)
        elif query.data.startswith("shop_buy_"):
            await shop_buy_handler(query.data, update, context)
        elif query.data == "shop_main":
            await shop_main_handler(update, context)
        elif query.data == "shop_refresh":
            await shop_main_handler(update, context)
        else:
            await query.answer("❌ Unknown shop action!")
            
    except Exception as e:
        logger.error(f"Shop callback handler error: {e}")
        await query.answer("❌ Shop error! Please try again!")


# Dictionary mapping callback data patterns to handlers
CALLBACK_HANDLERS = {
    "catch_": catch_button_handler,
    "already_caught": already_caught_handler,
    "shop_": shop_callback_handler,
}


async def inline_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route inline callback queries to appropriate handlers."""
    query = update.callback_query
    
    try:
        # Find matching handler
        for pattern, handler in CALLBACK_HANDLERS.items():
            if query.data.startswith(pattern) or query.data == pattern:
                await handler(update, context)
                return
        
        # No handler found
        await query.answer("❌ Unknown action!", show_alert=True)
        
    except Exception as e:
        logger.error(f"Inline callback router error: {e}")
        await query.answer("❌ Error processing action!", show_alert=True)
