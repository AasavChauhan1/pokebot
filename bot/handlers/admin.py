"""Admin command handlers."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.user_service import user_service
from bot.services.pokemon_service import pokemon_service
from bot.services.spawn_service import spawn_service
from bot.utils.helpers import is_admin, format_coins

logger = logging.getLogger(__name__)


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin command for admin panel."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use admin commands.")
        return
    
    try:
        if not context.args:
            # Show admin help
            admin_text = """
🔧 **Admin Panel**

**Available Commands:**
• `/admin stats` - View bot statistics
• `/admin user <user_id>` - View user info
• `/admin give <user_id> <pokemon_id>` - Give Pokémon to user
• `/admin coins <user_id> <amount>` - Add/remove coins
• `/admin cleanup` - Clean expired spawns
• `/admin broadcast <message>` - Send message to all users
• `/admin ban <user_id>` - Ban user
• `/admin unban <user_id>` - Unban user

**Examples:**
• `/admin stats`
• `/admin user 123456789`
• `/admin give 123456789 25`
• `/admin coins 123456789 1000`
            """
            
            await update.message.reply_text(admin_text, parse_mode='Markdown')
            return
        
        command = context.args[0].lower()
        
        if command == "stats":
            await _admin_stats(update, context)
        elif command == "user" and len(context.args) >= 2:
            await _admin_user_info(update, context)
        elif command == "give" and len(context.args) >= 3:
            await _admin_give_pokemon(update, context)
        elif command == "coins" and len(context.args) >= 3:
            await _admin_manage_coins(update, context)
        elif command == "cleanup":
            await _admin_cleanup(update, context)
        else:
            await update.message.reply_text("❌ Invalid admin command. Use `/admin` for help.")
            
    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        await update.message.reply_text("❌ An error occurred while processing admin command.")


async def _admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics."""
    try:
        from config.database import db
        
        # Get user count
        user_count = await db.db.users.count_documents({})
        
        # Get Pokémon count
        pokemon_count = await db.db.pokemon.count_documents({})
        
        # Get spawn stats
        spawn_stats = await spawn_service.get_spawn_stats()
        
        # Get battle count
        battle_count = await db.db.battles.count_documents({})
        
        # Get trade count
        trade_count = await db.db.trades.count_documents({})
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:** {user_count:,}
🐾 **Total Pokémon:** {pokemon_count:,}
⚔️ **Battles:** {battle_count:,}
🔄 **Trades:** {trade_count:,}

🌟 **Spawn Stats:**
• Total Spawns: {spawn_stats.get('total_spawns', 0):,}
• Caught: {spawn_stats.get('caught_spawns', 0):,}
• Shiny Spawns: {spawn_stats.get('shiny_spawns', 0):,}
• Catch Rate: {spawn_stats.get('catch_rate', 0):.1%}
• Average Level: {spawn_stats.get('average_level', 0)}

📈 **Database Size:**
• Users Collection: {user_count:,} documents
• Pokémon Collection: {pokemon_count:,} documents
• Spawns Collection: {spawn_stats.get('total_spawns', 0):,} documents
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        await update.message.reply_text("❌ Error retrieving statistics.")


async def _admin_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed user information."""
    try:
        user_id = int(context.args[1])
        
        # Get user stats
        stats = await user_service.get_user_stats(user_id)
        if not stats:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        user_data = stats["user"]
        
        user_info = f"""
👤 **User Information**

**Basic Info:**
• User ID: `{user_data.user_id}`
• Username: @{user_data.username or 'None'}
• Name: {user_data.first_name or 'Unknown'} {user_data.last_name or ''}
• Language: {user_data.language}

**Trainer Stats:**
• Level: {user_data.trainer_level}
• Experience: {user_data.experience:,} XP
• Coins: {format_coins(user_data.coins)}

**Collection:**
• Total Pokémon: {stats['pokemon_count']}
• Shiny Pokémon: {stats['shiny_count']}
• Pokémon Caught: {user_data.pokemon_caught}

**Battle Stats:**
• Wins: {user_data.battles_won}
• Losses: {user_data.battles_lost}
• Win Rate: {stats.get('win_rate', 0):.1f}%

**Activity:**
• Daily Streak: {user_data.daily_streak}
• Last Daily: {user_data.last_daily_claim or 'Never'}
• Joined: {user_data.created_at.strftime('%Y-%m-%d')}
        """
        
        await update.message.reply_text(user_info, parse_mode='Markdown')
        
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid user ID format.")
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        await update.message.reply_text("❌ Error retrieving user information.")


async def _admin_give_pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Give a Pokémon to a user."""
    try:
        user_id = int(context.args[1])
        pokemon_species_id = int(context.args[2])
        
        # Optional level and shiny parameters
        level = 1
        is_shiny = False
        
        if len(context.args) > 3:
            level = int(context.args[3])
        if len(context.args) > 4:
            is_shiny = context.args[4].lower() in ['true', '1', 'yes', 'shiny']
        
        # Ensure user exists
        user = await user_service.get_user(user_id)
        if not user:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        # Create Pokémon
        pokemon = await pokemon_service.create_pokemon(
            owner_id=user_id,
            species_id=pokemon_species_id,
            level=level,
            is_shiny=is_shiny
        )
        
        if pokemon:
            await update.message.reply_text(
                f"✅ Successfully gave {pokemon.species.title()} "
                f"(Level {pokemon.level}{'✨' if pokemon.is_shiny else ''}) to user {user_id}."
            )
        else:
            await update.message.reply_text("❌ Failed to create Pokémon.")
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid command format. Use: `/admin give <user_id> <pokemon_id> [level] [shiny]`")
    except Exception as e:
        logger.error(f"Error giving Pokémon: {e}")
        await update.message.reply_text("❌ Error giving Pokémon.")


async def _admin_manage_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add or remove coins from a user."""
    try:
        user_id = int(context.args[1])
        amount = int(context.args[2])
        
        # Check if user exists
        user = await user_service.get_user(user_id)
        if not user:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        # Add coins
        success = await user_service.add_coins(user_id, amount)
        
        if success:
            action = "Added" if amount > 0 else "Removed"
            await update.message.reply_text(
                f"✅ {action} {abs(amount):,} coins {'to' if amount > 0 else 'from'} user {user_id}."
            )
        else:
            await update.message.reply_text("❌ Failed to update coins.")
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid command format. Use: `/admin coins <user_id> <amount>`")
    except Exception as e:
        logger.error(f"Error managing coins: {e}")
        await update.message.reply_text("❌ Error managing coins.")


async def _admin_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clean up expired spawns."""
    try:
        cleaned = await spawn_service.cleanup_expired_spawns()
        await update.message.reply_text(f"✅ Cleaned up {cleaned} expired spawns.")
        
    except Exception as e:
        logger.error(f"Error in admin cleanup: {e}")
        await update.message.reply_text("❌ Error during cleanup.")
