"""Setup script for the Pokémon bot."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.database import db
from config.settings import settings


async def setup_database():
    """Set up database connections and indexes."""
    print("🔧 Setting up database...")
    
    try:
        # Connect to databases
        await db.connect()
        print("✅ Connected to MongoDB and Redis")
        
        # Create indexes
        await db.create_indexes()
        print("✅ Database indexes created")
        
        print("🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)
    
    finally:
        await db.disconnect()


def create_env_file():
    """Create .env file from example if it doesn't exist."""
    env_path = project_root / ".env"
    env_example_path = project_root / ".env.example"
    
    if not env_path.exists() and env_example_path.exists():
        print("📝 Creating .env file from example...")
        
        with open(env_example_path, 'r') as example_file:
            content = example_file.read()
        
        with open(env_path, 'w') as env_file:
            env_file.write(content)
        
        print("✅ .env file created. Please edit it with your actual values.")
        return True
    
    return False


def check_requirements():
    """Check if all requirements are installed."""
    print("📦 Checking requirements...")
    
    try:
        import telegram
        import motor
        import redis
        import aiohttp
        import decouple
        import pydantic
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False


def check_configuration():
    """Check if configuration is valid."""
    print("⚙️ Checking configuration...")
    
    try:
        # Try to load settings
        bot_token = settings.BOT_TOKEN
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            print("❌ BOT_TOKEN not configured")
            print("💡 Please set your Telegram bot token in .env file")
            return False
        
        print("✅ Configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def main():
    """Main setup function."""
    print("🚀 PokéBot Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if create_env_file():
        print("⚠️  Please edit the .env file with your configuration before continuing.")
        sys.exit(0)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    if not check_configuration():
        sys.exit(1)
    
    # Setup database
    await setup_database()
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 You can now start the bot with: python main.py")
    print("\n📚 Quick start commands:")
    print("   • /start - Start your journey")
    print("   • /spawn - Spawn a Pokémon")
    print("   • /catch - Catch a Pokémon")
    print("   • /help - Get help")


if __name__ == "__main__":
    asyncio.run(main())
