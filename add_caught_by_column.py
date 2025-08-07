"""Quick database update for inline buttons."""

import asyncio
import asyncpg
from config.settings import settings

async def add_caught_by_column():
    """Add caught_by column to spawns table."""
    try:
        # Connect to database using DATABASE_URL
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Check if column already exists
        result = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'spawns' AND column_name = 'caught_by'
            )
        """)
        
        if not result:
            # Add caught_by column
            await conn.execute("""
                ALTER TABLE spawns 
                ADD COLUMN caught_by BIGINT DEFAULT NULL
            """)
            print("✅ Added caught_by column to spawns table")
        else:
            print("✅ caught_by column already exists")
        
        await conn.close()
        print("✅ Database update complete!")
        
    except Exception as e:
        print(f"❌ Database update error: {e}")

if __name__ == "__main__":
    asyncio.run(add_caught_by_column())
