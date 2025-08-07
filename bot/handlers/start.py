"""Professional start command handler."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Professional start command with modern onboarding."""
    user = update.effective_user
    
    try:
        # Modern welcome message
        welcome_message = f"""🌟 **Welcome to PokéBot, {user.first_name}!** 🌟

🤖 **The Most Advanced Pokémon Bot Experience**

**🚀 Getting Started:**
1️⃣ **`/daily`** - Claim your welcome bonus (100+ coins)
2️⃣ **`/spawn`** - Find your first wild Pokémon
3️⃣ **`/catch`** - Capture it with 98% success rate
4️⃣ **`/pokemon`** - View your growing collection

**⚡ What Makes Us Special:**
• **Ultra-Fast Performance** - Lightning speed operations
• **Real Pokémon Images** - Authentic sprites and artwork
• **Auto-Spawning System** - Wild Pokémon appear every 30-60s
• **Professional Interface** - Clean, modern UI design
• **High Success Rates** - Optimized catching mechanics

**💰 Reward System:**
• **Daily Rewards:** 100-600 coins every 5 hours
• **Streak Bonuses:** Up to +500 coins for consistency
• **Milestone Rewards:** Special bonuses at 7, 14, 30 days

**� Core Features:**
• **Collection System:** Catch and organize your Pokémon
• **Team Building:** Create your perfect 6-Pokémon team
• **Rarity System:** Common to Legendary classifications
• **Shiny Variants:** Ultra-rare special editions

**📱 Quick Actions:**
• Type **`/help`** for complete command reference
• Join group chats for automatic spawning
• Start building your dream team today!

**Ready to become a Pokémon Master? Your journey starts now!** 🎮

*Pro Tip: Use `/daily` first to get starting coins!*"""
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text(
            "🎉 **Welcome to PokéBot!**\n\n"
            "Your Pokémon adventure begins now!\n"
            "Use `/help` to see all available commands."
        )
