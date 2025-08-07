"""Database migration script for PostgreSQL setup."""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import Database
from config.settings import Settings
from bot.models.sql_models import Base
from sqlalchemy import text
import asyncpg

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize the PostgreSQL database with tables."""
    
    settings = Settings()
    database = Database()
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL database...")
        await database.connect()
        
        # Create all tables
        logger.info("Creating database tables...")
        await database.create_tables()
        
        logger.info("Database initialization completed successfully!")
        
        # Verify tables were created
        async with database.engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Created tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await database.disconnect()


async def test_database_connection():
    """Test the database connection and basic operations."""
    
    settings = Settings()
    database = Database()
    
    try:
        logger.info("Testing database connection...")
        await database.connect()
        
        # Test basic query using SQLAlchemy
        async with database.engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"PostgreSQL version: {version}")
        
        logger.info("Database connection test successful!")
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise
    finally:
        await database.disconnect()


async def main():
    """Main migration function."""
    try:
        # Test connection first
        await test_database_connection()
        
        # Initialize database
        await init_database()
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1)
