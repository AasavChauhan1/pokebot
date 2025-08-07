"""Database configuration and connection management for PostgreSQL."""

import logging
from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy base
Base = declarative_base()


class Database:
    """Database connection manager for PostgreSQL."""
    
    def __init__(self):
        self.engine = None
        self.async_session = None
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Connect to PostgreSQL."""
        try:
            # Create SQLAlchemy async engine with optimized settings
            self.engine = create_async_engine(
                settings.ASYNC_DATABASE_URL,
                echo=False,  # Disable SQL logging for performance
                pool_pre_ping=True,
                pool_recycle=1800,  # Recycle connections every 30 minutes
                pool_size=20,  # Increase pool size
                max_overflow=30,  # Allow more overflow connections
                pool_timeout=10,  # Faster timeout
                connect_args={
                    "server_settings": {
                        "application_name": "pokemon_bot",
                        "jit": "off",  # Disable JIT for faster small queries
                    }
                }
            )
            
            # Create session factory
            self.async_session = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info("Connected to PostgreSQL successfully")
            
            # Create asyncpg pool with SSL options
            import urllib.parse
            parsed = urllib.parse.urlparse(settings.DATABASE_URL)
            
            # Extract connection parameters
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            user = parsed.username
            password = parsed.password
            
            # Create asyncpg pool with optimized settings
            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                ssl='require',
                min_size=10,  # Minimum connections
                max_size=50,  # Maximum connections
                max_queries=50000,  # Max queries per connection
                max_inactive_connection_lifetime=300,  # 5 minutes
                command_timeout=10,  # 10 seconds timeout
                server_settings={
                    'application_name': 'pokemon_bot_fast',
                    'tcp_keepalives_idle': '600',
                    'tcp_keepalives_interval': '30',
                    'tcp_keepalives_count': '3',
                }
            )
            logger.info("AsyncPG pool created successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Disconnected from PostgreSQL")
        
        if self.pool:
            await self.pool.close()
            logger.info("Closed AsyncPG pool")
    
    async def create_tables(self) -> None:
        """Create database tables."""
        try:
            from bot.models.sql_models import Base
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
    
    def get_session(self) -> AsyncSession:
        """Get database session."""
        if not self.async_session:
            raise RuntimeError("Database not connected")
        return self.async_session()
    
    async def execute_raw(self, query: str, *args):
        """Execute raw SQL query using asyncpg."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)


# Global database instance
db = Database()
