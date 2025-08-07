"""Daily rewards handler - ultra fast version with pure SQL."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.fast_daily_service import fast_daily_service

logger = logging.getLogger(__name__)


async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /daily command for claiming daily rewards - ultra fast."""
    user = update.effective_user
    
    try:
        # Check if user exists and their daily status
        status = await fast_daily_service.get_user_daily_status(user.id)
        
        # Create new user if doesn't exist
        if not status["exists"]:
            success = await fast_daily_service.create_new_user(
                user.id, user.username, user.first_name, user.last_name
            )
            
            if success:
                await update.message.reply_text(
                    "� **Welcome to PokéBot!**\n\n"
                    "🎁 **Welcome Bonus Received:**\n"
                    "💰 +100 coins\n"
                    "🔥 Daily streak: Day 1\n\n"
                    "� **Daily Rewards:**\n"
                    "• Return every 5 hours for rewards\n"
                    "• Longer streaks = bigger bonuses\n"
                    "• Maximum streak bonus: +500 coins\n\n"
                    "🎯 Use `/help` to see all commands!"
                )
            else:
                await update.message.reply_text(
                    "❌ **Registration Error**\n\n"
                    "Please try the `/daily` command again."
                )
            return
        
        # Check if already claimed today
        if not status["can_claim"]:
            await update.message.reply_text(
                f"⏰ **Daily Reward Already Claimed**\n\n"
                f"🕐 **Next reward available in:** {status['hours_left']} hours\n"
                f"🔥 **Current streak:** {status['streak']} days\n"
                f"💰 **Current balance:** {status['coins']:,} coins\n\n"
                f"📊 **Streak Rewards:**\n"
                f"• Base reward: 100 coins\n"
                f"• Streak bonus: +{min(status['streak'] * 20, 500)} coins\n"
                f"• Next reward: {100 + min((status['streak'] + 1) * 20, 500)} coins"
            )
            return
        
        # Claim the daily reward
        result = await fast_daily_service.claim_daily_reward(user.id)
        
        if not result["success"]:
            if result["reason"] == "already_claimed":
                await update.message.reply_text(
                    f"⏰ **Already Claimed Today**\n\n"
                    f"Come back in {result.get('hours_left', 'a few')} hours for your next reward!"
                )
            else:
                await update.message.reply_text(
                    "❌ **Daily Reward Error**\n\n"
                    "Please try again in a moment."
                )
            return
        
        # Success! Build professional response message
        message = f"🎉 **Daily Reward Claimed!**\n\n"
        message += f"💰 **Base reward:** +{result['base_reward']} coins\n"
        
        if result['streak_bonus'] > 0:
            message += f"🔥 **Streak bonus:** +{result['streak_bonus']} coins\n"
        
        message += f"💎 **Total earned:** +{result['total_reward']} coins\n"
        message += f"� **Current streak:** {result['new_streak']} days\n\n"
        
        # Streak motivation messages
        new_streak = result['new_streak']
        if new_streak == 1:
            message += "🌟 **Streak started!** Come back daily for bigger rewards!"
        elif new_streak < 5:
            message += f"🚀 **{5-new_streak} more days** for 200+ coin rewards!"
        elif new_streak < 10:
            message += f"🔥 **{10-new_streak} more days** for 300+ coin rewards!"
        elif new_streak < 25:
            message += f"⭐ **{25-new_streak} more days** for maximum rewards!"
        else:
            message += "👑 **LEGENDARY STREAK!** Maximum daily rewards achieved!"
        
        message += f"\n\n💡 **Next reward:** {100 + min((new_streak + 1) * 20, 500)} coins in 5 hours"
        
        await update.message.reply_text(message)
        
        # Special milestone celebrations
        if result["is_milestone"]:
            if new_streak == 7:
                await update.message.reply_text(
                    "🎊 **7-DAY MILESTONE ACHIEVED!**\n\n"
                    "🎁 You're now eligible for weekly bonus events!\n"
                    "🍬 Special items will be available soon!"
                )
            elif new_streak == 14:
                await update.message.reply_text(
                    "🌟 **14-DAY CHAMPION!**\n\n"
                    "⚡ Experience boost activated!\n"
                    "🎯 Higher shiny encounter rates!"
                )
            elif new_streak == 30:
                await update.message.reply_text(
                    "💎 **30-DAY LEGEND!**\n\n"
                    "✨ **LEGENDARY STATUS ACHIEVED!**\n"
                    "🌈 Exclusive shiny boost permanently activated!\n"
                    "👑 You are a true Pokémon Master!"
                )
            
    except Exception as e:
        logger.error(f"Error in daily command: {e}")
        await update.message.reply_text(
            "❌ **Service Temporarily Unavailable**\n\n"
            "Please try again in a moment."
        )
