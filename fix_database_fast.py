"""Quick database fix for spawn issues."""

import asyncio
import asyncpg
from config.settings import settings


async def fix_spawns_table():
    """Fix spawns table for proper enum support."""
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        print("🔧 Fixing spawns table...")
        
        # Drop and recreate spawns table with correct structure
        await conn.execute("DROP TABLE IF EXISTS spawns CASCADE")
        await conn.execute("DROP TYPE IF EXISTS pokemonrarity CASCADE")
        
        # Create spawns table with proper enum
        await conn.execute("""
            CREATE TYPE pokemonrarity AS ENUM (
                'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythical'
            )
        """)
        
        await conn.execute("""
            CREATE TABLE spawns (
                id SERIAL PRIMARY KEY,
                spawn_id VARCHAR(50) UNIQUE NOT NULL,
                chat_id BIGINT NOT NULL,
                species VARCHAR(100) NOT NULL,
                species_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                is_shiny BOOLEAN DEFAULT FALSE,
                rarity pokemonrarity NOT NULL,
                spawned_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP NOT NULL,
                is_caught BOOLEAN DEFAULT FALSE,
                caught_by BIGINT NULL,
                caught_at TIMESTAMP NULL
            )
        """)
        
        # Create indexes for performance
        await conn.execute("CREATE INDEX idx_spawns_chat_id ON spawns(chat_id)")
        await conn.execute("CREATE INDEX idx_spawns_active ON spawns(chat_id, is_caught, expires_at)")
        
        print("✅ Spawns table fixed!")
        
        # Also fix users table if needed
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    coins INTEGER DEFAULT 1000,
                    experience INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    pokemon_caught INTEGER DEFAULT 0,
                    total_pokemon INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    last_daily_claim TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
            print("✅ Users table ensured!")
            
        except Exception as e:
            print(f"Users table: {e}")
        
        await conn.close()
        print("🚀 Database is ready for FAST spawning!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(fix_spawns_table())
