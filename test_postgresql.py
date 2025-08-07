"""Simple test to verify PostgreSQL connection and service functionality."""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import db
from config.settings import Settings
from bot.models.sql_models import User
from sqlalchemy import select

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_postgresql_operations():
    """Test basic PostgreSQL operations."""
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL...")
        await db.connect()
        
        # Test creating a user
        logger.info("Testing user creation...")
        async with db.get_session() as session:
            # Check if test user already exists
            result = await session.execute(
                select(User).where(User.user_id == 123456789)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info("Test user already exists")
                test_user = existing_user
            else:
                # Create test user
                test_user = User(
                    user_id=123456789,
                    username="test_user",
                    first_name="Test",
                    last_name="User",
                    trainer_level=1,
                    experience=0,
                    coins=1000,
                    total_pokemon=0,
                    pokemon_caught=0,
                    pokemon_seen=0,
                    battles_won=0,
                    battles_lost=0,
                    battles_total=0,
                    daily_streak=0,
                    language="en",
                    notifications_enabled=True
                )
                
                session.add(test_user)
                await session.commit()
                logger.info("Test user created successfully")
        
        # Test reading the user
        logger.info("Testing user retrieval...")
        async with db.get_session() as session:
            result = await session.execute(
                select(User).where(User.user_id == 123456789)
            )
            retrieved_user = result.scalar_one_or_none()
            
            if retrieved_user:
                logger.info(f"Retrieved user: {retrieved_user.username} (Level {retrieved_user.trainer_level})")
            else:
                logger.error("Failed to retrieve test user")
        
        # Test count query
        logger.info("Testing count query...")
        async with db.get_session() as session:
            from sqlalchemy import func
            result = await session.execute(select(func.count(User.id)))
            user_count = result.scalar()
            logger.info(f"Total users in database: {user_count}")
        
        logger.info("PostgreSQL test completed successfully!")
        
    except Exception as e:
        logger.error(f"PostgreSQL test failed: {e}")
        raise
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(test_postgresql_operations())
