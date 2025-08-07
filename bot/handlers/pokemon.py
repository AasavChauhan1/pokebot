"""Pokémon and team management handlers."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.pokemon_service import pokemon_service
from bot.services.user_service import user_service
from bot.services.pokeapi import pokeapi
from bot.utils.helpers import format_pokemon_name, get_rarity_emoji, get_type_emoji

logger = logging.getLogger(__name__)


async def pokemon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pokemon command to show user's collection."""
    user = update.effective_user
    
    try:
        # Get page number from arguments
        page = 1
        if context.args:
            try:
                page = max(1, int(context.args[0]))
            except ValueError:
                pass
        
        # Pagination settings
        per_page = 10
        skip = (page - 1) * per_page
        
        # Get user's Pokémon
        pokemon_list = await pokemon_service.get_user_pokemon(user.id, skip, per_page)
        
        if not pokemon_list:
            if page == 1:
                await update.message.reply_text(
                    "🔍 Your Pokédex is empty! Use `/spawn` and `/catch` to start your collection!"
                )
            else:
                await update.message.reply_text("📄 No Pokémon found on this page.")
            return
        
        # Get total count for pagination
        total_count = await pokemon_service.get_pokemon_stats_summary(user.id)
        total_count = total_count.get("total", 0)
        total_pages = (total_count + per_page - 1) // per_page
        
        # Build Pokémon list
        pokemon_text = f"📚 **Your Pokédex** (Page {page}/{total_pages})\n\n"
        
        for i, pokemon in enumerate(pokemon_list, skip + 1):
            rarity_emoji = get_rarity_emoji(pokemon.rarity)
            name = format_pokemon_name(pokemon.species, pokemon.nickname, pokemon.is_shiny)
            team_indicator = "⭐" if pokemon.in_team else ""
            
            pokemon_text += (
                f"**{i}.** {rarity_emoji} {name} {team_indicator}\n"
                f"   └ Level {pokemon.level} • {pokemon.nature.title()} • {pokemon.ability.title()}\n\n"
            )
        
        # Create navigation keyboard
        keyboard = []
        nav_row = []
        
        if page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"pokemon_page_{page-1}"))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"pokemon_page_{page+1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        # Add action buttons
        keyboard.append([
            InlineKeyboardButton("👥 View Team", callback_data="view_team"),
            InlineKeyboardButton("📊 Stats", callback_data="pokemon_stats")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            pokemon_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in pokemon command: {e}")
        await update.message.reply_text("❌ An error occurred while loading your Pokémon.")


async def team_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /team command to show and manage team."""
    user = update.effective_user
    
    try:
        # Get user's team
        team = await pokemon_service.get_user_team(user.id)
        
        if not team:
            await update.message.reply_text(
                "👥 **Your Team is Empty!**\n\n"
                "Use `/pokemon` to view your collection and add Pokémon to your team.\n"
                "You can have up to 6 Pokémon in your active team for battles."
            )
            return
        
        team_text = "👥 **Your Battle Team**\n\n"
        
        for i, pokemon in enumerate(team, 1):
            rarity_emoji = get_rarity_emoji(pokemon.rarity)
            name = format_pokemon_name(pokemon.species, pokemon.nickname, pokemon.is_shiny)
            
            # Get Pokémon types
            types = await pokeapi.get_pokemon_types(pokemon.species_id)
            type_emojis = " ".join(get_type_emoji(t) for t in types[:2])  # Max 2 types
            
            team_text += (
                f"**{i}.** {rarity_emoji} {name}\n"
                f"   └ Level {pokemon.level} • {type_emojis} • HP: {pokemon.hp}\n"
                f"   └ ATK: {pokemon.attack} • DEF: {pokemon.defense} • SPD: {pokemon.speed}\n\n"
            )
        
        # Add team stats
        avg_level = sum(p.level for p in team) / len(team)
        total_hp = sum(p.hp for p in team)
        
        team_text += f"📊 **Team Stats:**\n"
        team_text += f"• Average Level: **{avg_level:.1f}**\n"
        team_text += f"• Total HP: **{total_hp}**\n"
        team_text += f"• Team Size: **{len(team)}/6**"
        
        # Create management keyboard
        keyboard = [
            [InlineKeyboardButton("➕ Add Pokémon", callback_data="team_add")],
            [InlineKeyboardButton("➖ Remove Pokémon", callback_data="team_remove")],
            [InlineKeyboardButton("🔄 Rearrange", callback_data="team_rearrange")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            team_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in team command: {e}")
        await update.message.reply_text("❌ An error occurred while loading your team.")


async def catch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ultra-fast catch handler using pure SQL."""
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        from bot.services.fast_spawn_service import fast_spawn_service
        
        # Get active spawn
        spawn = await fast_spawn_service.get_active_spawn(chat.id)
        
        if not spawn:
            await update.message.reply_text(
                "🔍 **No Wild Pokémon Found**\n\n"
                "Use `/spawn` to spawn a Pokémon instantly!\n"
                "🔄 Auto-spawns happen every 30-60 seconds."
            )
            return
        
        # Attempt catch
        success, message = await fast_spawn_service.catch_spawn(spawn['spawn_id'], user.id)
        
        if success:
            # Success message with professional formatting
            rarity_emoji = "✨" if spawn['is_shiny'] else get_rarity_emoji(spawn['rarity'])
            name = f"✨ {spawn['species'].title()}" if spawn['is_shiny'] else spawn['species'].title()
            
            success_text = f"🎉 **POKÉMON CAPTURED!**\n\n"
            success_text += f"{rarity_emoji} **{name}** (Level {spawn['level']})\n"
            
            if spawn['is_shiny']:
                success_text += "\n✨ **RARE SHINY CAPTURED!** ✨\n"
            
            success_text += f"\n💬 {message}\n"
            success_text += f"\n� Use `/pokemon` to view your collection\n"
            success_text += f"👥 Use `/team` to manage your battle team\n"
            success_text += f"🔄 More wild Pokémon spawn automatically!"
            
            # Send with image if available
            if spawn.get('image_url'):
                await update.message.reply_photo(
                    photo=spawn['image_url'],
                    caption=success_text,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(success_text, parse_mode='Markdown')
        else:
            # Enhanced failure message
            failure_text = f"💨 **Capture Failed!**\n\n"
            failure_text += f"🎯 {message}\n"
            failure_text += f"� **Tip:** Higher level Pokémon are harder to catch!\n"
            failure_text += f"🔄 Keep trying - the Pokémon is still here!"
            
            await update.message.reply_text(failure_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Catch handler error: {e}")
        await update.message.reply_text(
            "❌ **Capture System Error**\n\n"
            "Please try catching again!\n"
            "🔄 The Pokémon is still available."
        )
