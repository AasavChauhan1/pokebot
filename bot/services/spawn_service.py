"""Spawn service for managing Pokémon spawns."""

import logging
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select, update, delete, func
from bot.models.sql_models import Spawn, PokemonRarity, SpawnCooldown
from bot.services.pokeapi import pokeapi
from bot.services.pokemon_service import pokemon_service
from bot.services.user_service import user_service
from bot.utils.helpers import (
    generate_id, determine_rarity, calculate_shiny_chance,
    get_legendary_pokemon, get_rare_pokemon
)
from config.database import db
from config.settings import settings

logger = logging.getLogger(__name__)


class SpawnService:
    """Service for managing Pokémon spawns - optimized for speed."""
    
    def __init__(self):
        # Cache for frequent operations
        self._pokemon_cache = {}
        self._species_cache = {}
        self._last_cache_clear = datetime.utcnow()
    
    async def _clear_cache_if_needed(self):
        """Clear cache every 30 minutes for memory management."""
        if (datetime.utcnow() - self._last_cache_clear).seconds > 1800:
            self._pokemon_cache.clear()
            self._species_cache.clear()
            self._last_cache_clear = datetime.utcnow()
    
    async def _get_cached_pokemon_data(self, species_id: int) -> Optional[Dict]:
        """Get cached Pokemon data or fetch from API."""
        if species_id in self._pokemon_cache:
            return self._pokemon_cache[species_id]
        
        data = await pokeapi.get_pokemon_data(species_id)
        if data:
            self._pokemon_cache[species_id] = data
        return data
    
    async def create_spawn(self, chat_id: int) -> Optional[Spawn]:
        """Create a new Pokémon spawn - optimized for speed."""
        try:
            await self._clear_cache_if_needed()
            
            # Fast check for existing spawn using raw query
            async with db.pool.acquire() as conn:
                existing = await conn.fetchval(
                    "SELECT 1 FROM spawns WHERE chat_id = $1 AND is_caught = FALSE AND expires_at > $2 LIMIT 1",
                    chat_id, datetime.utcnow()
                )
                if existing:
                    return None  # Already has active spawn
                
                # Fast random Pokemon generation
                species_id = random.randint(1, 1010)  # Use known Pokemon range
                level = random.randint(1, 50)
                is_shiny = random.random() < 0.002  # 0.2% shiny chance - faster than helper
                rarity = PokemonRarity.RARE if is_shiny else PokemonRarity.COMMON  # Use enum values
                
                # Get cached species name
                pokemon_data = await self._get_cached_pokemon_data(species_id)
                if not pokemon_data:
                    species_id = random.randint(1, 151)  # Fallback to Gen 1
                    pokemon_data = await self._get_cached_pokemon_data(species_id)
                    if not pokemon_data:
                        return None
                
                species_name = pokemon_data['name']
                spawn_id = generate_id("spawn_")
                now = datetime.utcnow()
                expires = now + timedelta(minutes=8)  # Faster expiry for more action
                
                # Fast database insert using raw query
                await conn.execute("""
                    INSERT INTO spawns (spawn_id, chat_id, species, species_id, level, 
                                       is_shiny, rarity, spawned_at, expires_at, is_caught)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, spawn_id, chat_id, species_name, species_id, level, 
                is_shiny, rarity, now, expires, False)
                
                # Create spawn object to return
                spawn = Spawn(
                    spawn_id=spawn_id,
                    chat_id=chat_id,
                    species=species_name,
                    species_id=species_id,
                    level=level,
                    is_shiny=is_shiny,
                    rarity=rarity,
                    spawned_at=now,
                    expires_at=expires,
                    is_caught=False
                )
                
                logger.info(f"Fast spawn: {species_name} in chat {chat_id}")
                return spawn
            
        except Exception as e:
            logger.error(f"Error creating spawn: {e}")
            return None
    
    async def get_active_spawn(self, chat_id: int) -> Optional[Spawn]:
        """Get active spawn in a chat - optimized for speed."""
        try:
            # Fast query using raw SQL
            async with db.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT spawn_id, chat_id, species, species_id, level, is_shiny, 
                           rarity, spawned_at, expires_at, is_caught, caught_by, caught_at
                    FROM spawns 
                    WHERE chat_id = $1 AND is_caught = FALSE AND expires_at > $2
                    ORDER BY spawned_at DESC 
                    LIMIT 1
                """, chat_id, datetime.utcnow())
                
                if row:
                    return Spawn(
                        spawn_id=row['spawn_id'],
                        chat_id=row['chat_id'],
                        species=row['species'],
                        species_id=row['species_id'],
                        level=row['level'],
                        is_shiny=row['is_shiny'],
                        rarity=row['rarity'],
                        spawned_at=row['spawned_at'],
                        expires_at=row['expires_at'],
                        is_caught=row['is_caught'],
                        caught_by=row['caught_by'],
                        caught_at=row['caught_at']
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting active spawn: {e}")
            return None
    
    async def catch_spawn(self, spawn_id: str, user_id: int) -> tuple[bool, Optional[str]]:
        """Attempt to catch a spawned Pokémon - optimized for speed."""
        try:
            # Fast transaction using raw SQL
            async with db.pool.acquire() as conn:
                async with conn.transaction():
                    # Get spawn info in one query
                    spawn_row = await conn.fetchrow("""
                        SELECT spawn_id, chat_id, species, species_id, level, is_shiny, 
                               rarity, is_caught, expires_at
                        FROM spawns 
                        WHERE spawn_id = $1
                    """, spawn_id)
                    
                    if not spawn_row:
                        return False, "Spawn not found"
                    
                    # Quick checks
                    if spawn_row['is_caught']:
                        return False, "This Pokémon has already been caught!"
                    
                    if spawn_row['expires_at'] < datetime.utcnow():
                        return False, "This Pokémon has fled!"
                    
                    # Fast catch rate - simplified for speed (higher success rate)
                    catch_rate = 0.95 if spawn_row['rarity'] == "common" else 0.90 if spawn_row['rarity'] == "rare" else 0.85
                    
                    # Fast catch attempt
                    if random.random() > catch_rate:
                        return False, "The Pokémon broke free!"
                    
                    # Mark spawn as caught instantly
                    await conn.execute("""
                        UPDATE spawns 
                        SET is_caught = TRUE, caught_by = $2, caught_at = $3
                        WHERE spawn_id = $1
                    """, spawn_id, user_id, datetime.utcnow())
                    
                    # Fast Pokemon creation using direct insert
                    pokemon_id = generate_id("poke_")
                    level = spawn_row['level']
                    await conn.execute("""
                        INSERT INTO pokemon (pokemon_id, owner_id, species, species_id, 
                                           level, experience, hp, attack, defense, special_attack, 
                                           special_defense, speed, nature, ability, is_shiny, 
                                           rarity, gender, created_at, in_team, team_position)
                        VALUES ($1, $2, $3, $4, $5, 0, 
                               ($5 * 2 + 100), ($5 * 2 + 50), ($5 * 2 + 50), ($5 * 2 + 50),
                               ($5 * 2 + 50), ($5 * 2 + 50), 'hardy', 'unknown', $6,
                               $7, 'unknown', $8, FALSE, NULL)
                    """, pokemon_id, user_id, spawn_row['species'], spawn_row['species_id'], 
                    level, spawn_row['is_shiny'], spawn_row['rarity'], datetime.utcnow())
                    
                    # Fast user stats update
                    await conn.execute("""
                        UPDATE users 
                        SET pokemon_caught = pokemon_caught + 1, 
                            total_pokemon = total_pokemon + 1,
                            experience = experience + $2
                        WHERE user_id = $1
                    """, user_id, level * 10)  # Fast exp calculation
                    
                    logger.info(f"Fast catch: User {user_id} caught {spawn_row['species']}")
                    return True, pokemon_id
                    
        except Exception as e:
            logger.error(f"Error catching spawn: {e}")
            return False, "An error occurred while catching"
    
    def _get_catch_rate(self, rarity: PokemonRarity) -> float:
        """Get catch rate based on rarity."""
        rates = {
            PokemonRarity.COMMON: 0.9,
            PokemonRarity.UNCOMMON: 0.75,
            PokemonRarity.RARE: 0.6,
            PokemonRarity.EPIC: 0.4,
            PokemonRarity.LEGENDARY: 0.25,
            PokemonRarity.MYTHICAL: 0.1
        }
        return rates.get(rarity, 0.8)
    
    def _calculate_catch_exp(self, rarity: PokemonRarity, level: int) -> int:
        """Calculate experience reward for catching."""
        base_exp = {
            PokemonRarity.COMMON: 10,
            PokemonRarity.UNCOMMON: 20,
            PokemonRarity.RARE: 35,
            PokemonRarity.EPIC: 50,
            PokemonRarity.LEGENDARY: 75,
            PokemonRarity.MYTHICAL: 100
        }
        
        return base_exp.get(rarity, 10) + (level // 5)
    
    async def _get_random_pokemon_id(self) -> int:
        """Get a random Pokémon ID with weighted rarity."""
        # Define rarity weights
        legendary_chance = 0.01  # 1%
        rare_chance = 0.05       # 5%
        uncommon_chance = 0.15   # 15%
        # Common: 79%
        
        roll = random.random()
        
        if roll < legendary_chance:
            # Legendary Pokémon
            legendaries = get_legendary_pokemon()
            return random.choice(legendaries)
        elif roll < legendary_chance + rare_chance:
            # Rare Pokémon
            rares = get_rare_pokemon()
            return random.choice(rares)
        elif roll < legendary_chance + rare_chance + uncommon_chance:
            # Uncommon (starters, etc.)
            # Gen 1-5 starters and their evolutions
            starters = list(range(1, 10)) + list(range(152, 161)) + list(range(252, 261))
            return random.choice(starters)
        else:
            # Common Pokémon (most others)
            return random.randint(1, 649)  # Gen 1-5
    
    async def check_spawn_cooldown(self, chat_id: int) -> bool:
        """Check if spawn cooldown has passed."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SpawnCooldown).where(SpawnCooldown.chat_id == chat_id)
                )
                cooldown = result.scalar_one_or_none()
                
                if not cooldown:
                    return True
                
                return datetime.utcnow() >= cooldown.cooldown_until
            
        except Exception as e:
            logger.error(f"Error checking spawn cooldown: {e}")
            return True
    
    async def set_spawn_cooldown(self, chat_id: int) -> None:
        """Set spawn cooldown for a chat."""
        try:
            async with db.get_session() as session:
                now = datetime.utcnow()
                cooldown_until = now + timedelta(seconds=settings.SPAWN_COOLDOWN)
                
                # Check if cooldown record exists
                result = await session.execute(
                    select(SpawnCooldown).where(SpawnCooldown.chat_id == chat_id)
                )
                cooldown = result.scalar_one_or_none()
                
                if cooldown:
                    # Update existing
                    cooldown.last_spawn = now
                    cooldown.cooldown_until = cooldown_until
                else:
                    # Create new
                    cooldown = SpawnCooldown(
                        chat_id=chat_id,
                        last_spawn=now,
                        cooldown_until=cooldown_until
                    )
                    session.add(cooldown)
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error setting spawn cooldown: {e}")
    
    async def should_auto_spawn(self, chat_id: int) -> bool:
        """Determine if a Pokémon should auto-spawn."""
        # Random chance for auto-spawn (5% per message)
        if random.random() > 0.05:
            return False
        
        # Check cooldown
        if not await self.check_spawn_cooldown(chat_id):
            return False
        
        # Check if there's already an active spawn
        active_spawn = await self.get_active_spawn(chat_id)
        if active_spawn:
            return False
        
        return True
    
    async def cleanup_expired_spawns(self) -> int:
        """Clean up expired spawns."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    delete(Spawn).where(
                        Spawn.is_caught == False,
                        Spawn.expires_at < datetime.utcnow()
                    )
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired spawns")
                
                return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up spawns: {e}")
            return 0
    
    async def get_spawn_stats(self, chat_id: int = None) -> Dict[str, Any]:
        """Get spawn statistics."""
        try:
            async with db.get_session() as session:
                # Base query
                query = select(
                    func.count(Spawn.id).label('total_spawns'),
                    func.sum(func.cast(Spawn.is_caught, db.engine.dialect.INTEGER)).label('caught_spawns'),
                    func.sum(func.cast(Spawn.is_shiny, db.engine.dialect.INTEGER)).label('shiny_spawns'),
                    func.avg(Spawn.level).label('avg_level')
                )
                
                if chat_id:
                    query = query.where(Spawn.chat_id == chat_id)
                
                result = await session.execute(query)
                row = result.fetchone()
                
                if row:
                    total_spawns = row.total_spawns or 0
                    caught_spawns = row.caught_spawns or 0
                    shiny_spawns = row.shiny_spawns or 0
                    avg_level = row.avg_level or 0
                    
                    return {
                        "total_spawns": total_spawns,
                        "caught_spawns": caught_spawns,
                        "shiny_spawns": shiny_spawns,
                        "catch_rate": caught_spawns / max(total_spawns, 1),
                        "average_level": round(avg_level, 1)
                    }
                
                return {"total_spawns": 0, "caught_spawns": 0, "shiny_spawns": 0, "catch_rate": 0, "average_level": 0}
            
        except Exception as e:
            logger.error(f"Error getting spawn stats: {e}")
            return {}


# Global service instance
spawn_service = SpawnService()
