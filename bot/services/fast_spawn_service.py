"""Ultra-fast pure SQL spawn service - no ORM conflicts."""

import logging
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.database import db
from config.settings import settings

logger = logging.getLogger(__name__)


class RawSQLSpawnService:
    """Pure SQL spawn service - maximum speed, zero conflicts."""
    
    def __init__(self):
        self._spawn_cache = {}
        self._pokemon_names = [
            'pikachu', 'charizard', 'blastoise', 'venusaur', 'mewtwo', 'mew',
            'lugia', 'ho-oh', 'celebi', 'kyogre', 'groudon', 'rayquaza',
            'dialga', 'palkia', 'giratina', 'arceus', 'reshiram', 'zekrom',
            'squirtle', 'bulbasaur', 'charmander', 'eevee', 'vaporeon',
            'jolteon', 'flareon', 'espeon', 'umbreon', 'leafeon', 'glaceon',
            'sylveon', 'lucario', 'garchomp', 'dragonite', 'tyranitar',
            'salamence', 'metagross', 'latios', 'latias', 'darkrai', 'cresselia'
        ]
    
    async def create_spawn(self, chat_id: int) -> bool:
        """Create instant spawn with pure SQL - ultra fast."""
        try:
            async with db.pool.acquire() as conn:
                # Check for existing active spawn
                existing = await conn.fetchval("""
                    SELECT id FROM spawns 
                    WHERE chat_id = $1 AND is_caught = false AND expires_at > NOW()
                """, chat_id)
                
                if existing:
                    return False  # Already has spawn
                
                # Fast Pokemon generation
                species_name = random.choice(self._pokemon_names)
                species_id = random.randint(1, 800)
                level = random.randint(1, 50)
                is_shiny = random.random() < 0.005  # 0.5% chance
                rarity = 'legendary' if is_shiny else random.choice(['common', 'uncommon', 'rare'])
                
                spawn_id = f"spawn_{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}"
                expires_at = datetime.utcnow() + timedelta(minutes=10)
                
                # Direct insert - no ORM overhead
                await conn.execute("""
                    INSERT INTO spawns (spawn_id, chat_id, species, species_id, level, is_shiny, rarity, spawned_at, expires_at, is_caught)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), $8, false)
                """, spawn_id, chat_id, species_name, species_id, level, is_shiny, rarity, expires_at)
                
                # Cache for quick access
                self._spawn_cache[chat_id] = {
                    'spawn_id': spawn_id,
                    'species': species_name,
                    'level': level,
                    'is_shiny': is_shiny,
                    'rarity': rarity
                }
                
                logger.info(f"FAST SPAWN: {species_name} (lvl {level}) in chat {chat_id}")
                return True
                
        except Exception as e:
            logger.error(f"Fast spawn error: {e}")
            return False
    
    async def get_active_spawn(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get active spawn ultra fast."""
        try:
            # Check cache first
            if chat_id in self._spawn_cache:
                cached = self._spawn_cache[chat_id]
                # Add image URL to cached data
                try:
                    from bot.services.pokeapi import pokeapi
                    image_url = await pokeapi.get_pokemon_sprite_url(
                        cached.get('species_id', 1), 
                        cached.get('is_shiny', False)
                    )
                    cached['image_url'] = image_url
                except:
                    cached['image_url'] = None
                return cached
            
            async with db.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT spawn_id, species, species_id, level, is_shiny, rarity, spawned_at
                    FROM spawns 
                    WHERE chat_id = $1 AND is_caught = false AND expires_at > NOW()
                    ORDER BY spawned_at DESC LIMIT 1
                """, chat_id)
                
                if row:
                    spawn_data = {
                        'spawn_id': row['spawn_id'],
                        'species': row['species'],
                        'species_id': row['species_id'],
                        'level': row['level'],
                        'is_shiny': row['is_shiny'],
                        'rarity': row['rarity'],
                        'spawned_at': row['spawned_at']
                    }
                    
                    # Get Pokemon image URL
                    try:
                        from bot.services.pokeapi import pokeapi
                        image_url = await pokeapi.get_pokemon_sprite_url(
                            row['species_id'], 
                            row['is_shiny']
                        )
                        spawn_data['image_url'] = image_url
                    except:
                        spawn_data['image_url'] = None
                    
                    # Update cache
                    self._spawn_cache[chat_id] = spawn_data
                    return spawn_data
                
                return None
                
        except Exception as e:
            logger.error(f"Get spawn error: {e}")
            return None
    
    async def get_spawn_by_id(self, spawn_id: str) -> Optional[Dict[str, Any]]:
        """Get spawn details by spawn_id for inline buttons."""
        try:
            async with db.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT spawn_id, species, species_id, level, is_shiny, rarity, spawned_at, is_caught, caught_by
                    FROM spawns 
                    WHERE spawn_id = $1 AND expires_at > NOW()
                """, spawn_id)
                
                if row:
                    spawn_data = {
                        'spawn_id': row['spawn_id'],
                        'species': row['species'],
                        'species_id': row['species_id'],
                        'level': row['level'],
                        'is_shiny': row['is_shiny'],
                        'rarity': row['rarity'],
                        'spawned_at': row['spawned_at'],
                        'is_caught': row['is_caught'],
                        'caught_by': row['caught_by']
                    }
                    
                    # Get Pokemon image URL
                    try:
                        from bot.services.pokeapi import pokeapi
                        image_url = await pokeapi.get_pokemon_sprite_url(
                            row['species_id'], 
                            row['is_shiny']
                        )
                        spawn_data['image_url'] = image_url
                    except:
                        spawn_data['image_url'] = None
                    
                    return spawn_data
                return None
                
        except Exception as e:
            logger.error(f"Error getting spawn by ID: {e}")
            return None
    
    async def catch_spawn(self, spawn_id: str, user_id: int) -> tuple[bool, str]:
        """Ultra-fast catch with pure SQL."""
        try:
            async with db.pool.acquire() as conn:
                async with conn.transaction():
                    # Get spawn details
                    spawn = await conn.fetchrow("""
                        SELECT spawn_id, chat_id, species, species_id, level, is_shiny, rarity, is_caught, caught_by
                        FROM spawns WHERE spawn_id = $1 AND expires_at > NOW()
                    """, spawn_id)
                    
                    if not spawn:
                        return False, "This Pokémon has disappeared!"
                    
                    # Check if already caught
                    if spawn['is_caught']:
                        return False, f"Already caught by someone else!"
                    
                    # 98% success rate for fast gameplay
                    if random.random() > 0.02:
                        # Mark as caught
                        await conn.execute("""
                            UPDATE spawns 
                            SET is_caught = true, caught_by = $2, caught_at = NOW()
                            WHERE spawn_id = $1
                        """, spawn_id, user_id)
                        
                        # Ensure user exists
                        await conn.execute("""
                            INSERT INTO users (user_id, username, first_name, coins, experience, level, pokemon_caught, total_pokemon)
                            VALUES ($1, 'trainer', 'Unknown', 1000, 0, 1, 0, 0)
                            ON CONFLICT (user_id) DO NOTHING
                        """, user_id)
                        
                        # Create Pokemon entry
                        pokemon_id = f"poke_{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}"
                        await conn.execute("""
                            INSERT INTO pokemon (pokemon_id, owner_id, species, species_id, level, is_shiny, rarity, nature, ability, hp, attack, defense, special_attack, special_defense, speed, caught_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, 'hardy', 'unknown', $8, $9, $10, $11, $12, $13, NOW())
                        """, pokemon_id, user_id, spawn['species'], spawn['species_id'], spawn['level'], spawn['is_shiny'], spawn['rarity'],
                        spawn['level'] * 3 + 50,  # HP
                        spawn['level'] * 2 + 30,  # Attack  
                        spawn['level'] * 2 + 30,  # Defense
                        spawn['level'] * 2 + 30,  # Sp Attack
                        spawn['level'] * 2 + 30,  # Sp Defense
                        spawn['level'] * 2 + 30   # Speed
                        )
                        
                        # Update user stats
                        exp_gained = spawn['level'] * 10
                        coins_earned = spawn['level'] * 5 + (100 if spawn['is_shiny'] else 0)
                        await conn.execute("""
                            UPDATE users 
                            SET pokemon_caught = pokemon_caught + 1,
                                total_pokemon = total_pokemon + 1,
                                experience = experience + $2,
                                coins = coins + $3
                            WHERE user_id = $1
                        """, user_id, exp_gained, coins_earned)
                        
                        # Clear cache
                        if spawn['chat_id'] in self._spawn_cache:
                            del self._spawn_cache[spawn['chat_id']]
                        
                        bonus_text = f" (+{coins_earned} coins)" if coins_earned > 0 else ""
                        return True, f"Caught {spawn['species']}! (+{exp_gained} EXP{bonus_text})"
                    else:
                        return False, f"{spawn['species']} escaped! Try again!"
                        
        except Exception as e:
            logger.error(f"Catch error: {e}")
            return False, "Catch failed!"
    
    async def cleanup_expired(self) -> int:
        """Fast cleanup of expired spawns."""
        try:
            async with db.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM spawns 
                    WHERE expires_at < NOW() AND is_caught = false
                """)
                # Clear cache for expired spawns
                self._spawn_cache.clear()
                return int(result.split()[-1]) if result else 0
        except:
            return 0


# Global service
fast_spawn_service = RawSQLSpawnService()
