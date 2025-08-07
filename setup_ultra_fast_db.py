"""Final database setup for ultra-fast bot."""

import asyncio
import asyncpg
from config.settings import settings


async def setup_fast_database():
    """Setup optimized database for maximum speed."""
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        print("🔧 Setting up ULTRA-FAST database...")
        
        # Drop all existing tables for clean start
        await conn.execute("DROP TABLE IF EXISTS user_pokemon CASCADE")
        await conn.execute("DROP TABLE IF EXISTS spawns CASCADE")
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")
        await conn.execute("DROP TYPE IF EXISTS pokemonrarity CASCADE")
        
        # Create rarity enum
        await conn.execute("""
            CREATE TYPE pokemonrarity AS ENUM (
                'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythical'
            )
        """)
        
        # Create users table
        await conn.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255) DEFAULT 'trainer',
                first_name VARCHAR(255) DEFAULT 'Unknown',
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
        
        # Create spawns table
        await conn.execute("""
            CREATE TABLE spawns (
                id SERIAL PRIMARY KEY,
                spawn_id VARCHAR(100) UNIQUE NOT NULL,
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
        
        # Create user_pokemon table
        await conn.execute("""
            CREATE TABLE user_pokemon (
                id SERIAL PRIMARY KEY,
                pokemon_id VARCHAR(100) UNIQUE NOT NULL,
                user_id BIGINT NOT NULL,
                species VARCHAR(100) NOT NULL,
                species_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                is_shiny BOOLEAN DEFAULT FALSE,
                rarity pokemonrarity NOT NULL,
                nature VARCHAR(50) DEFAULT 'hardy',
                ability VARCHAR(100) DEFAULT 'unknown',
                hp INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                special_attack INTEGER NOT NULL,
                special_defense INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                nickname VARCHAR(100) NULL,
                in_team BOOLEAN DEFAULT FALSE,
                team_position INTEGER NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create performance indexes
        await conn.execute("CREATE INDEX idx_users_user_id ON users(user_id)")
        await conn.execute("CREATE INDEX idx_spawns_chat_active ON spawns(chat_id, is_caught, expires_at)")
        await conn.execute("CREATE INDEX idx_spawns_spawn_id ON spawns(spawn_id)")
        await conn.execute("CREATE INDEX idx_user_pokemon_user_id ON user_pokemon(user_id)")
        await conn.execute("CREATE INDEX idx_user_pokemon_team ON user_pokemon(user_id, in_team)")
        
        print("✅ ULTRA-FAST database ready!")
        print("✅ All tables created with optimized indexes!")
        print("✅ Pure SQL service compatible!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")


if __name__ == "__main__":
    asyncio.run(setup_fast_database())
