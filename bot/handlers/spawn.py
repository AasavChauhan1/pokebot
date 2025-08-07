"""Ultra-fast spawn handlers using pure SQL service."""

import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.fast_spawn_service import fast_spawn_service
from bot.services.scheduler_service import scheduler_service
from bot.utils.helpers import format_pokemon_name, get_rarity_emoji, is_admin

logger = logging.getLogger(__name__)

# Simple in-memory cooldown tracking
user_cooldowns = {}


async def spawn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ultra-fast manual spawn handler."""
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        # Register for auto-spawning
        scheduler_service.register_channel(chat.id)
        
        # Simple cooldown (non-admins only)
        if not is_admin(user.id):
            cooldown_key = f"spawn_{user.id}"
            now = time.time()
            if cooldown_key in user_cooldowns:
                if now - user_cooldowns[cooldown_key] < 30:  # 30 second cooldown
                    remaining = 30 - int(now - user_cooldowns[cooldown_key])
                    await update.message.reply_text(
                        f"⏰ **Spawn Cooldown Active**\n\n"
                        f"Please wait {remaining} seconds before manual spawning.\n\n"
                        f"💡 **Tip:** Auto-spawns happen every 30-60 seconds!\n"
                        f"🔄 No need to manually spawn frequently."
                    )
                    return
            user_cooldowns[cooldown_key] = now
        
        # Check for existing spawn
        active = await fast_spawn_service.get_active_spawn(chat.id)
        if active:
            name = format_pokemon_name(active['species'], None, active['is_shiny'])
            rarity_emoji = get_rarity_emoji(active['rarity'])
            
            message = f"🌟 **Wild Pokémon Spotted!**\n\n"
            message += f"{rarity_emoji} **{name}** (Level {active['level']})\n"
            
            if active['is_shiny']:
                message += "\n✨ **SHINY POKÉMON!** ✨\n"
            
            message += f"\n🎯 Type `/catch` to capture it!"
            
            # Create inline catch button
            keyboard = [[
                InlineKeyboardButton("🎯 Catch Now!", callback_data=f"catch_{active['spawn_id']}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send with image if available
            if active.get('image_url'):
                await update.message.reply_photo(
                    photo=active['image_url'],
                    caption=message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            return
        
        # Create new spawn
        success = await fast_spawn_service.create_spawn(chat.id)
        
        if not success:
            await update.message.reply_text(
                "❌ **Spawn Failed**\n\n"
                "🔄 Auto-spawns are active every 30-60 seconds!\n"
                "⏰ Please wait for the next automatic spawn."
            )
            return
        
        # Get spawn details
        spawn = await fast_spawn_service.get_active_spawn(chat.id)
        if not spawn:
            await update.message.reply_text(
                "❌ **Spawn Creation Error**\n\n"
                "🔄 Auto-spawns are active every 30-60 seconds!"
            )
            return
        
        # Professional spawn message
        name = format_pokemon_name(spawn['species'], None, spawn['is_shiny'])
        rarity_emoji = get_rarity_emoji(spawn['rarity'])
        
        message = f"🌟 **Pokémon Spawned Successfully!**\n\n"
        message += f"{rarity_emoji} **{name}** (Level {spawn['level']})\n"
        
        if spawn['is_shiny']:
            message += "\n✨ **RARE SHINY POKÉMON!** ✨\n"
        
        message += f"\n🎯 Type `/catch` to capture it!\n"
        message += f"⏰ Expires in 10 minutes\n"
        message += f"🔄 Auto-spawns every 30-60 seconds"
        
        # Create inline catch button
        keyboard = [[
            InlineKeyboardButton("🎯 Catch Now!", callback_data=f"catch_{spawn['spawn_id']}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send with image if available
        if spawn.get('image_url'):
            await update.message.reply_photo(
                photo=spawn['image_url'],
                caption=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
    except Exception as e:
        logger.error(f"Spawn handler error: {e}")
        await update.message.reply_text(
            "❌ **Spawn Service Error**\n\n"
            "🔄 Auto-spawns are still active!\n"
            "⏰ Next spawn in 30-60 seconds."
        )


async def auto_spawn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple auto-spawn for group messages."""
    chat = update.effective_chat
    
    try:
        # Only in groups
        if chat.type not in ['group', 'supergroup']:
            return
        
        # Random chance (3% per message)
        if not (hash(str(chat.id) + str(time.time())) % 100 < 3):
            return
        
        # Check existing spawn
        active = await fast_spawn_service.get_active_spawn(chat.id)
        if active:
            return
        
        # Create spawn
        success = await fast_spawn_service.create_spawn(chat.id)
        if not success:
            return
        
        # Get details and announce
        spawn = await fast_spawn_service.get_active_spawn(chat.id)
        if spawn:
            name = format_pokemon_name(spawn['species'], None, spawn['is_shiny'])
            rarity_emoji = get_rarity_emoji(spawn['rarity'])
            
            message = f"🌿 **A wild Pokémon appeared!**\n\n"
            message += f"{rarity_emoji} **{name}** (Level {spawn['level']})\n"
            
            if spawn['is_shiny']:
                message += "\n✨ **SHINY POKÉMON!** ✨\n"
            
            message += f"\n🎯 Quick! Use `/catch` to capture it!\n"
            message += f"⏰ Disappears in 10 minutes"
            
            # Create inline catch button
            keyboard = [[
                InlineKeyboardButton("🎯 Catch Now!", callback_data=f"catch_{spawn['spawn_id']}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send with image if available
            if spawn.get('image_url'):
                await update.message.reply_photo(
                    photo=spawn['image_url'],
                    caption=message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
    except Exception as e:
        logger.error(f"Auto-spawn error: {e}")
        # Silent fail for auto-spawns
