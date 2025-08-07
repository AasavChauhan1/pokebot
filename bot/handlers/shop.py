"""Shop system for purchasing items and upgrades."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.user_service import user_service
from bot.services.pokemon_service import pokemon_service

logger = logging.getLogger(__name__)

# Shop items with prices and descriptions
SHOP_ITEMS = {
    "pokeball": {
        "name": "Poké Ball",
        "emoji": "⚪",
        "price": 100,
        "description": "Basic ball for catching Pokémon",
        "category": "catching"
    },
    "greatball": {
        "name": "Great Ball", 
        "emoji": "🔵",
        "price": 300,
        "description": "Better ball with higher catch rate",
        "category": "catching"
    },
    "ultraball": {
        "name": "Ultra Ball",
        "emoji": "⚫", 
        "price": 800,
        "description": "Advanced ball for difficult catches",
        "category": "catching"
    },
    "rare_candy": {
        "name": "Rare Candy",
        "emoji": "🍭",
        "price": 1000,
        "description": "Instantly level up any Pokémon",
        "category": "items"
    },
    "exp_share": {
        "name": "Exp. Share",
        "emoji": "📚",
        "price": 2000,
        "description": "Share experience with your team",
        "category": "items"
    },
    "lucky_egg": {
        "name": "Lucky Egg",
        "emoji": "🥚",
        "price": 3000,
        "description": "Double experience for 1 hour",
        "category": "items"
    },
    "incense": {
        "name": "Incense",
        "emoji": "🔥",
        "price": 500,
        "description": "Increase spawn rates for 30 minutes",
        "category": "items"
    },
    "shiny_charm": {
        "name": "Shiny Charm",
        "emoji": "✨",
        "price": 10000,
        "description": "Slightly increase shiny chances",
        "category": "premium"
    }
}

CATEGORIES = {
    "catching": "🎯 Catching Items",
    "items": "📦 Utility Items", 
    "premium": "💎 Premium Items"
}


async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shop command to show the shop interface."""
    user = update.effective_user
    
    try:
        # Get user's balance
        user_data = await user_service.get_or_create_user(user.id, user.username)
        balance = user_data.coins if user_data else 0
        
        # Show shop categories
        shop_text = "🏪 **Pokémon Shop**\n\n"
        shop_text += f"💰 **Your Balance:** {balance:,} coins\n\n"
        shop_text += "**Categories:**\n"
        
        for category_id, category_name in CATEGORIES.items():
            item_count = len([item for item in SHOP_ITEMS.values() if item['category'] == category_id])
            shop_text += f"{category_name} ({item_count} items)\n"
        
        shop_text += "\n💡 **How to earn coins:**\n"
        shop_text += "• Daily rewards (`/daily`)\n"
        shop_text += "• Catching Pokémon\n"
        shop_text += "• Completing challenges\n"
        shop_text += "• Battle victories"
        
        # Create category keyboard
        keyboard = []
        for category_id, category_name in CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(category_name, callback_data=f"shop_category_{category_id}")])
        
        keyboard.append([InlineKeyboardButton("🔄 Refresh Balance", callback_data="shop_refresh")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            shop_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in shop command: {e}")
        await update.message.reply_text(
            "❌ **Shop Temporarily Unavailable**\n\n"
            "Please try again later!"
        )


async def shop_category_handler(query_data: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle shop category selection."""
    category_id = query_data.replace("shop_category_", "")
    user = update.effective_user
    
    try:
        # Get user's balance
        user_data = await user_service.get_or_create_user(user.id, user.username)
        balance = user_data.coins if user_data else 0
        
        # Filter items by category
        category_items = {k: v for k, v in SHOP_ITEMS.items() if v['category'] == category_id}
        
        if not category_items:
            await update.callback_query.answer("❌ No items in this category!")
            return
        
        category_name = CATEGORIES.get(category_id, "Unknown Category")
        
        shop_text = f"🏪 **{category_name}**\n\n"
        shop_text += f"💰 **Your Balance:** {balance:,} coins\n\n"
        
        # List items
        for item_id, item in category_items.items():
            affordability = "✅" if balance >= item['price'] else "❌"
            shop_text += f"{affordability} {item['emoji']} **{item['name']}**\n"
            shop_text += f"   💰 {item['price']:,} coins\n"
            shop_text += f"   📝 {item['description']}\n\n"
        
        # Create item purchase keyboard
        keyboard = []
        for item_id, item in category_items.items():
            if balance >= item['price']:
                keyboard.append([InlineKeyboardButton(
                    f"Buy {item['emoji']} {item['name']} ({item['price']:,} coins)",
                    callback_data=f"shop_buy_{item_id}"
                )])
        
        # Navigation buttons
        keyboard.append([InlineKeyboardButton("🔙 Back to Shop", callback_data="shop_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            shop_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in shop category: {e}")
        await update.callback_query.answer("❌ Error loading category!")


async def shop_buy_handler(query_data: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle item purchase."""
    item_id = query_data.replace("shop_buy_", "")
    user = update.effective_user
    
    try:
        # Validate item
        if item_id not in SHOP_ITEMS:
            await update.callback_query.answer("❌ Invalid item!")
            return
        
        item = SHOP_ITEMS[item_id]
        
        # Get user's balance
        user_data = await user_service.get_or_create_user(user.id, user.username)
        balance = user_data.coins if user_data else 0
        
        # Check if user can afford it
        if balance < item['price']:
            await update.callback_query.answer(
                f"❌ Not enough coins! Need {item['price']:,} coins, you have {balance:,}."
            )
            return
        
        # Process purchase
        new_balance = balance - item['price']
        await user_service.update_user_coins(user.id, new_balance)
        
        # Add item to inventory (simplified - just show success)
        success_text = f"✅ **Purchase Successful!**\n\n"
        success_text += f"{item['emoji']} **{item['name']}** purchased!\n"
        success_text += f"💰 **Cost:** {item['price']:,} coins\n"
        success_text += f"💳 **New Balance:** {new_balance:,} coins\n\n"
        
        # Special handling for certain items
        if item_id == "rare_candy":
            success_text += "🍭 Use with `/use rare_candy [pokemon_id]` to level up!\n"
        elif item_id == "incense":
            success_text += "🔥 Use with `/use incense` to boost spawns!\n"
        elif item_id == "lucky_egg":
            success_text += "🥚 Use with `/use lucky_egg` for double XP!\n"
        else:
            success_text += f"📦 Added to your inventory!\n"
        
        success_text += "\n🛍️ Thank you for your purchase!"
        
        # Create continue shopping keyboard
        keyboard = [
            [InlineKeyboardButton("🛍️ Continue Shopping", callback_data=f"shop_category_{item['category']}")],
            [InlineKeyboardButton("🏪 Main Shop", callback_data="shop_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            success_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        await update.callback_query.answer("✅ Purchase successful!")
        
    except Exception as e:
        logger.error(f"Error in shop purchase: {e}")
        await update.callback_query.answer("❌ Purchase failed! Please try again.")


async def shop_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main shop."""
    user = update.effective_user
    
    try:
        # Get user's balance
        user_data = await user_service.get_or_create_user(user.id, user.username)
        balance = user_data.coins if user_data else 0
        
        # Show shop categories
        shop_text = "🏪 **Pokémon Shop**\n\n"
        shop_text += f"💰 **Your Balance:** {balance:,} coins\n\n"
        shop_text += "**Categories:**\n"
        
        for category_id, category_name in CATEGORIES.items():
            item_count = len([item for item in SHOP_ITEMS.values() if item['category'] == category_id])
            shop_text += f"{category_name} ({item_count} items)\n"
        
        shop_text += "\n💡 **How to earn coins:**\n"
        shop_text += "• Daily rewards (`/daily`)\n"
        shop_text += "• Catching Pokémon\n"
        shop_text += "• Completing challenges\n"
        shop_text += "• Battle victories"
        
        # Create category keyboard
        keyboard = []
        for category_id, category_name in CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(category_name, callback_data=f"shop_category_{category_id}")])
        
        keyboard.append([InlineKeyboardButton("🔄 Refresh Balance", callback_data="shop_refresh")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            shop_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error returning to main shop: {e}")
        await update.callback_query.answer("❌ Error loading shop!")
