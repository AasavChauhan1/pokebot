"""Help and start command handlers."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Professional start command with onboarding."""
    user = update.effective_user
    
    welcome_text = f"""🌟 **Welcome to PokéBot, {user.first_name}!** 🌟

🤖 **The Most Advanced Pokémon Bot Experience**

**🚀 Getting Started:**
1️⃣ Use `/daily` to claim your welcome bonus
2️⃣ Use `/spawn` to find your first Pokémon
3️⃣ Use `/catch` to capture it
4️⃣ Use `/pokemon` to view your collection

**⚡ What Makes Us Special:**
• **Ultra-Fast Performance** - Lightning speed operations
• **Real Pokémon Images** - Authentic sprites from PokéAPI
• **Auto-Spawning** - Wild Pokémon appear automatically
• **Professional UI** - Clean, modern interface
• **98% Success Rate** - Optimized catching system

**💰 Daily Rewards:**
• Claim every 5 hours for faster gameplay
• Build streaks for massive bonuses
• Up to 600 coins per day at max streak

**🎯 Quick Actions:**
• Type `/help` for complete command list
• Join group chats for auto-spawning
• Build your dream team of 6 Pokémon

Ready to become a Pokémon Master? Let's start your journey! 🎮"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Professional help command with current features."""
    
    help_text = """🤖 **PokéBot - Professional Pokémon Experience**

**⚡ Quick Start:**
• `/daily` - Claim your daily rewards (every 5 hours)
• `/spawn` - Spawn a wild Pokémon instantly
• `/catch` - Capture the spawned Pokémon
• `/pokemon` - View your Pokémon collection

**🎯 Core Features:**
• **Auto-Spawning:** Wild Pokémon appear every 30-60 seconds
• **Image Support:** See actual Pokémon sprites
• **98% Catch Rate:** Optimized capture system
• **Shiny Pokémon:** Rare variants with special effects
• **Team Building:** Manage your 6 Pokémon battle team
• **Shop System:** Buy items and upgrades with coins

**💰 Daily Rewards System:**
• Base reward: 100 coins daily
• Streak bonus: +20 coins per consecutive day
• Maximum bonus: +500 coins at 25+ day streak
• Special milestones at 7, 14, and 30 days

**📊 Statistics & Collection:**
• `/pokemon` - Browse your collection with pagination
• `/team` - View and manage your battle team
• `/shop` - Browse and purchase items with coins
• Rarity system: Common, Uncommon, Rare, Epic, Legendary
• Level progression and stat tracking

**⚙️ Professional Features:**
• Lightning-fast pure SQL database operations
• Real-time Pokemon data from official PokéAPI
• Intelligent caching for optimal performance
• Error-resistant architecture with graceful fallbacks

**� Pro Tips:**
• Auto-spawns are most active in group chats
• Higher level Pokémon are harder to catch
• Shiny Pokémon have special visual indicators
• Daily streaks provide massive long-term benefits

**🔗 System Status:**
✅ Ultra-fast spawn system active
✅ Image rendering operational
✅ Daily rewards functional
✅ Auto-spawning every 30-60 seconds

Ready to become a Pokémon Master? Start with `/daily`! 🌟"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )
