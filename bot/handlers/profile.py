"""Profile command handler."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.user_service import user_service
from bot.utils.helpers import format_coins, get_rarity_emoji
from bot.models import PokemonRarity

logger = logging.getLogger(__name__)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command."""
    user = update.effective_user
    
    try:
        # Get user stats
        stats = await user_service.get_user_stats(user.id)
        if not stats:
            await update.message.reply_text("❌ Profile not found. Use /start to begin your journey!")
            return
        
        user_data = stats["user"]
        
        # Calculate next level experience
        next_level_exp = stats.get("next_level_exp", 0)
        current_exp_in_level = user_data.experience - (user_data.trainer_level - 1) ** 3
        exp_for_current_level = user_data.trainer_level ** 3 - (user_data.trainer_level - 1) ** 3
        
        # Format win rate
        win_rate = round(stats.get("win_rate", 0), 1)
        
        # Daily streak status
        streak_text = f"🔥 {user_data.daily_streak} day(s)" if user_data.daily_streak > 0 else "❄️ No streak"
        
        profile_text = f"""
👤 **{user_data.first_name or 'Trainer'}'s Profile**

🎯 **Trainer Info:**
• Level: **{user_data.trainer_level}** 
• Experience: **{user_data.experience:,}** XP
• Next Level: **{next_level_exp:,}** XP needed
• Coins: **{format_coins(user_data.coins)}** 💰

🐾 **Pokémon Collection:**
• Total Pokémon: **{stats['pokemon_count']}**
• Caught: **{user_data.pokemon_caught}**
• Seen: **{user_data.pokemon_seen}**
• Shiny: **{stats['shiny_count']}** ✨

⚔️ **Battle Stats:**
• Wins: **{user_data.battles_won}**
• Losses: **{user_data.battles_lost}**
• Total: **{user_data.battles_total}**
• Win Rate: **{win_rate}%**

📅 **Activity:**
• Daily Streak: {streak_text}
• Member Since: {user_data.created_at.strftime('%B %Y')}

Use `/pokemon` to view your collection!
        """
        
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in profile command: {e}")
        await update.message.reply_text("❌ An error occurred while loading your profile.")
