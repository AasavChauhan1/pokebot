"""Fix Pokemon collection - update pokemon table and create proper collection system."""

import asyncio
import asyncpg
from config.settings import settings

async def fix_pokemon_collection():
    """Fix pokemon table structure and create proper collection system."""
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        print("🔧 Fixing Pokemon collection system...")
        
        # Drop existing pokemon table if exists (to start fresh)
        await conn.execute("DROP TABLE IF EXISTS pokemon CASCADE")
        print("✅ Dropped old pokemon table")
        
        # Create new pokemon table with proper structure
        await conn.execute("""
            CREATE TABLE pokemon (
                id SERIAL PRIMARY KEY,
                pokemon_id UUID DEFAULT gen_random_uuid(),
                owner_id BIGINT NOT NULL,
                species VARCHAR(50) NOT NULL,
                species_id INTEGER NOT NULL,
                nickname VARCHAR(50),
                level INTEGER NOT NULL DEFAULT 1,
                experience INTEGER NOT NULL DEFAULT 0,
                hp INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                special_attack INTEGER NOT NULL,
                special_defense INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                nature VARCHAR(20) NOT NULL,
                ability VARCHAR(50) NOT NULL,
                gender VARCHAR(10) DEFAULT 'Unknown',
                is_shiny BOOLEAN DEFAULT FALSE,
                rarity VARCHAR(20) NOT NULL DEFAULT 'Common',
                in_team BOOLEAN DEFAULT FALSE,
                team_position INTEGER,
                held_item VARCHAR(50),
                can_evolve BOOLEAN DEFAULT FALSE,
                evolution_stage INTEGER DEFAULT 1,
                caught_at TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Created new pokemon table with proper structure")
        
        # Create indexes for performance
        await conn.execute("CREATE INDEX idx_pokemon_owner ON pokemon(owner_id)")
        await conn.execute("CREATE INDEX idx_pokemon_species ON pokemon(species)")
        await conn.execute("CREATE INDEX idx_pokemon_team ON pokemon(owner_id, in_team)")
        print("✅ Created performance indexes")
        
        # Now migrate caught spawns to pokemon collection
        result = await conn.fetch("""
            SELECT s.spawn_id, s.species, s.species_id, s.level, s.is_shiny, s.rarity, s.caught_by, s.caught_at
            FROM spawns s
            WHERE s.is_caught = true AND s.caught_by IS NOT NULL
        """)
        
        print(f"📦 Found {len(result)} caught Pokemon to migrate...")
        
        for spawn in result:
            # Create pokemon from spawn
            await conn.execute("""
                INSERT INTO pokemon (
                    owner_id, species, species_id, level, is_shiny, rarity,
                    hp, attack, defense, special_attack, special_defense, speed,
                    nature, ability, caught_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6,
                    $7, $8, $9, $10, $11, $12,
                    $13, $14, $15
                )
            """, 
                spawn['caught_by'],  # owner_id
                spawn['species'],    # species
                spawn['species_id'], # species_id
                spawn['level'],      # level
                spawn['is_shiny'],   # is_shiny
                spawn['rarity'],     # rarity
                spawn['level'] * 10 + 50,  # hp (level-based)
                spawn['level'] * 2 + 20,   # attack
                spawn['level'] * 2 + 15,   # defense
                spawn['level'] * 2 + 18,   # special_attack
                spawn['level'] * 2 + 15,   # special_defense
                spawn['level'] * 2 + 10,   # speed
                'Hardy',             # nature (default)
                'Overgrow',          # ability (default)
                spawn['caught_at']   # caught_at
            )
        
        print(f"✅ Migrated {len(result)} Pokemon to collection!")
        
        await conn.close()
        print("🎉 Pokemon collection system fixed!")
        
    except Exception as e:
        print(f"❌ Error fixing pokemon collection: {e}")

if __name__ == "__main__":
    asyncio.run(fix_pokemon_collection())
