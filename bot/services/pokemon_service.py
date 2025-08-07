"""Pokémon service for managing Pokémon data."""

import logging
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import Pokemon, PokemonRarity
from bot.models.sql_models import Pokemon as SqlPokemon
from bot.services.pokeapi import pokeapi
from bot.utils.helpers import (
    generate_id, calculate_pokemon_stats, get_random_nature,
    determine_rarity, calculate_shiny_chance, get_level_from_exp
)
from config.database import db

logger = logging.getLogger(__name__)


class PokemonService:
    """Service for managing Pokémon data."""
    
    async def create_pokemon(self, owner_id: int, species_id: int, level: int = 1, is_shiny: bool = False) -> Optional[Pokemon]:
        """Create a new Pokémon."""
        try:
            # Get Pokémon data from PokeAPI
            pokemon_data = await pokeapi.get_pokemon_data(species_id)
            if not pokemon_data:
                logger.error(f"Could not fetch data for Pokémon {species_id}")
                return None
            
            species_name = pokemon_data['name']
            
            # Get base stats
            base_stats = await pokeapi.get_pokemon_stats(species_id)
            if not base_stats:
                logger.error(f"Could not fetch stats for Pokémon {species_id}")
                return None
            
            # Generate random attributes
            nature = get_random_nature()
            
            # Calculate actual stats based on level
            calculated_stats = calculate_pokemon_stats(base_stats, level, nature)
            
            # Get abilities and choose one randomly
            abilities = await pokeapi.get_pokemon_abilities(species_id)
            ability = random.choice(abilities) if abilities else "unknown"
            
            # Determine rarity
            rarity = determine_rarity(species_id, is_shiny)
            
            # Create Pokémon instance for API model
            pokemon = Pokemon(
                pokemon_id=generate_id("poke_"),
                owner_id=owner_id,
                species=species_name,
                species_id=species_id,
                level=level,
                experience=0,
                hp=calculated_stats.get('hp', 50),
                attack=calculated_stats.get('attack', 50),
                defense=calculated_stats.get('defense', 50),
                special_attack=calculated_stats.get('special_attack', 50),
                special_defense=calculated_stats.get('special_defense', 50),
                speed=calculated_stats.get('speed', 50),
                nature=nature,
                ability=ability,
                is_shiny=is_shiny,
                rarity=rarity,
                gender=random.choice(["male", "female", None])
            )
            
            # Create SQLAlchemy model for database
            sql_pokemon = SqlPokemon(
                pokemon_id=pokemon.pokemon_id,
                owner_id=pokemon.owner_id,
                species=pokemon.species,
                species_id=pokemon.species_id,
                level=pokemon.level,
                experience=pokemon.experience,
                hp=pokemon.hp,
                attack=pokemon.attack,
                defense=pokemon.defense,
                special_attack=pokemon.special_attack,
                special_defense=pokemon.special_defense,
                speed=pokemon.speed,
                nature=pokemon.nature,
                ability=pokemon.ability,
                is_shiny=pokemon.is_shiny,
                rarity=pokemon.rarity,
                gender=pokemon.gender
            )
            
            # Save to database
            async with db.get_session() as session:
                session.add(sql_pokemon)
                await session.commit()
                
            logger.info(f"Created Pokémon {species_name} for user {owner_id}")
            
            return pokemon
            
        except Exception as e:
            logger.error(f"Error creating Pokémon: {e}")
            return None
    
    async def get_pokemon(self, pokemon_id: str) -> Optional[Pokemon]:
        """Get Pokémon by ID."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon).where(SqlPokemon.pokemon_id == pokemon_id)
                )
                pokemon_data = result.scalar_one_or_none()
                
                if pokemon_data:
                    return Pokemon(
                        pokemon_id=pokemon_data.pokemon_id,
                        owner_id=pokemon_data.owner_id,
                        species=pokemon_data.species,
                        species_id=pokemon_data.species_id,
                        level=pokemon_data.level,
                        experience=pokemon_data.experience,
                        hp=pokemon_data.hp,
                        attack=pokemon_data.attack,
                        defense=pokemon_data.defense,
                        special_attack=pokemon_data.special_attack,
                        special_defense=pokemon_data.special_defense,
                        speed=pokemon_data.speed,
                        nature=pokemon_data.nature,
                        ability=pokemon_data.ability,
                        is_shiny=pokemon_data.is_shiny,
                        rarity=pokemon_data.rarity,
                        gender=pokemon_data.gender,
                        nickname=pokemon_data.nickname,
                        in_team=pokemon_data.in_team,
                        team_position=pokemon_data.team_position,
                        created_at=pokemon_data.created_at
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting Pokémon {pokemon_id}: {e}")
            return None
    
    async def get_user_pokemon(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Pokemon]:
        """Get user's Pokémon with pagination."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon)
                    .where(SqlPokemon.owner_id == user_id)
                    .offset(skip)
                    .limit(limit)
                )
                pokemon_data_list = result.scalars().all()
                
                pokemon_list = []
                for pokemon_data in pokemon_data_list:
                    pokemon_list.append(Pokemon(
                        pokemon_id=pokemon_data.pokemon_id,
                        owner_id=pokemon_data.owner_id,
                        species=pokemon_data.species,
                        species_id=pokemon_data.species_id,
                        level=pokemon_data.level,
                        experience=pokemon_data.experience,
                        hp=pokemon_data.hp,
                        attack=pokemon_data.attack,
                        defense=pokemon_data.defense,
                        special_attack=pokemon_data.special_attack,
                        special_defense=pokemon_data.special_defense,
                        speed=pokemon_data.speed,
                        nature=pokemon_data.nature,
                        ability=pokemon_data.ability,
                        is_shiny=pokemon_data.is_shiny,
                        rarity=pokemon_data.rarity,
                        gender=pokemon_data.gender,
                        nickname=pokemon_data.nickname,
                        in_team=pokemon_data.in_team,
                        team_position=pokemon_data.team_position,
                        created_at=pokemon_data.created_at
                    ))
                return pokemon_list
        except Exception as e:
            logger.error(f"Error getting user Pokémon for {user_id}: {e}")
            return []
    
    async def get_user_team(self, user_id: int) -> List[Pokemon]:
        """Get user's active team."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon)
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.in_team == True)
                    .order_by(SqlPokemon.team_position)
                )
                pokemon_data_list = result.scalars().all()
                
                team = []
                for pokemon_data in pokemon_data_list:
                    team.append(Pokemon(
                        pokemon_id=pokemon_data.pokemon_id,
                        owner_id=pokemon_data.owner_id,
                        species=pokemon_data.species,
                        species_id=pokemon_data.species_id,
                        level=pokemon_data.level,
                        experience=pokemon_data.experience,
                        hp=pokemon_data.hp,
                        attack=pokemon_data.attack,
                        defense=pokemon_data.defense,
                        special_attack=pokemon_data.special_attack,
                        special_defense=pokemon_data.special_defense,
                        speed=pokemon_data.speed,
                        nature=pokemon_data.nature,
                        ability=pokemon_data.ability,
                        is_shiny=pokemon_data.is_shiny,
                        rarity=pokemon_data.rarity,
                        gender=pokemon_data.gender,
                        nickname=pokemon_data.nickname,
                        in_team=pokemon_data.in_team,
                        team_position=pokemon_data.team_position,
                        created_at=pokemon_data.created_at
                    ))
                return team
        except Exception as e:
            logger.error(f"Error getting team for {user_id}: {e}")
            return []
    
    async def add_to_team(self, user_id: int, pokemon_id: str) -> bool:
        """Add Pokémon to user's team."""
        try:
            async with db.get_session() as session:
                # Check if team is full
                team_count_result = await session.execute(
                    select(func.count(SqlPokemon.id))
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.in_team == True)
                )
                team_count = team_count_result.scalar_one()
                
                if team_count >= 6:
                    return False
                
                # Check if Pokémon belongs to user
                pokemon_result = await session.execute(
                    select(SqlPokemon).where(SqlPokemon.pokemon_id == pokemon_id)
                )
                pokemon = pokemon_result.scalar_one_or_none()
                
                if not pokemon or pokemon.owner_id != user_id:
                    return False
                
                # Add to team
                position = team_count + 1
                await session.execute(
                    update(SqlPokemon)
                    .where(SqlPokemon.pokemon_id == pokemon_id)
                    .values(in_team=True, team_position=position)
                )
                await session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error adding Pokémon to team: {e}")
            return False
    
    async def remove_from_team(self, user_id: int, pokemon_id: str) -> bool:
        """Remove Pokémon from user's team."""
        try:
            async with db.get_session() as session:
                # Check if Pokémon belongs to user and is in team
                pokemon_result = await session.execute(
                    select(SqlPokemon).where(SqlPokemon.pokemon_id == pokemon_id)
                )
                pokemon = pokemon_result.scalar_one_or_none()
                
                if not pokemon or pokemon.owner_id != user_id or not pokemon.in_team:
                    return False
                
                # Remove from team
                await session.execute(
                    update(SqlPokemon)
                    .where(SqlPokemon.pokemon_id == pokemon_id)
                    .values(in_team=False, team_position=None)
                )
                await session.commit()
                
                # Reorder team positions
                await self._reorder_team_positions(user_id)
                return True
                
        except Exception as e:
            logger.error(f"Error removing Pokémon from team: {e}")
            return False
    
    async def _reorder_team_positions(self, user_id: int) -> None:
        """Reorder team positions after removal."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon)
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.in_team == True)
                    .order_by(SqlPokemon.team_position)
                )
                team_pokemon = result.scalars().all()
                
                for i, pokemon in enumerate(team_pokemon, 1):
                    await session.execute(
                        update(SqlPokemon)
                        .where(SqlPokemon.pokemon_id == pokemon.pokemon_id)
                        .values(team_position=i)
                    )
                await session.commit()
        except Exception as e:
            logger.error(f"Error reordering team positions: {e}")
    
    async def give_experience(self, pokemon_id: str, exp_amount: int) -> tuple[bool, bool, int]:
        """Give experience to Pokémon. Returns (success, leveled_up, new_level)."""
        try:
            async with db.get_session() as session:
                # Get current pokemon data
                pokemon_result = await session.execute(
                    select(SqlPokemon).where(SqlPokemon.pokemon_id == pokemon_id)
                )
                pokemon = pokemon_result.scalar_one_or_none()
                
                if not pokemon:
                    return False, False, 0
                
                old_level = pokemon.level
                new_exp = pokemon.experience + exp_amount
                new_level = get_level_from_exp(new_exp)
                
                leveled_up = new_level > old_level
                
                # If leveled up, recalculate stats
                update_data = {"experience": new_exp, "level": new_level}
                
                if leveled_up:
                    # Get base stats and recalculate
                    base_stats = await pokeapi.get_pokemon_stats(pokemon.species_id)
                    if base_stats:
                        new_stats = calculate_pokemon_stats(base_stats, new_level, pokemon.nature)
                        update_data.update({
                            "hp": new_stats.get('hp', pokemon.hp),
                            "attack": new_stats.get('attack', pokemon.attack),
                            "defense": new_stats.get('defense', pokemon.defense),
                            "special_attack": new_stats.get('special_attack', pokemon.special_attack),
                            "special_defense": new_stats.get('special_defense', pokemon.special_defense),
                            "speed": new_stats.get('speed', pokemon.speed),
                        })
                
                await session.execute(
                    update(SqlPokemon)
                    .where(SqlPokemon.pokemon_id == pokemon_id)
                    .values(**update_data)
                )
                await session.commit()
                
                return True, leveled_up, new_level
                
        except Exception as e:
            logger.error(f"Error giving experience to Pokémon {pokemon_id}: {e}")
            return False, False, 0
    
    async def set_nickname(self, user_id: int, pokemon_id: str, nickname: str) -> bool:
        """Set nickname for a Pokémon."""
        try:
            async with db.get_session() as session:
                # Check ownership
                pokemon_result = await session.execute(
                    select(SqlPokemon).where(SqlPokemon.pokemon_id == pokemon_id)
                )
                pokemon = pokemon_result.scalar_one_or_none()
                
                if not pokemon or pokemon.owner_id != user_id:
                    return False
                
                # Validate nickname length
                if len(nickname) > 20:
                    return False
                
                await session.execute(
                    update(SqlPokemon)
                    .where(SqlPokemon.pokemon_id == pokemon_id)
                    .values(nickname=nickname)
                )
                await session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error setting nickname: {e}")
            return False
    
    async def transfer_pokemon(self, pokemon_id: str, new_owner_id: int) -> bool:
        """Transfer Pokémon to new owner."""
        try:
            async with db.get_session() as session:
                await session.execute(
                    update(SqlPokemon)
                    .where(SqlPokemon.pokemon_id == pokemon_id)
                    .values(owner_id=new_owner_id, in_team=False, team_position=None)
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error transferring Pokémon: {e}")
            return False
    
    async def get_pokemon_by_species(self, user_id: int, species: str) -> List[Pokemon]:
        """Get user's Pokémon of a specific species."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon)
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.species == species.lower())
                )
                pokemon_data_list = result.scalars().all()
                
                pokemon_list = []
                for pokemon_data in pokemon_data_list:
                    pokemon_list.append(Pokemon(
                        pokemon_id=pokemon_data.pokemon_id,
                        owner_id=pokemon_data.owner_id,
                        species=pokemon_data.species,
                        species_id=pokemon_data.species_id,
                        level=pokemon_data.level,
                        experience=pokemon_data.experience,
                        hp=pokemon_data.hp,
                        attack=pokemon_data.attack,
                        defense=pokemon_data.defense,
                        special_attack=pokemon_data.special_attack,
                        special_defense=pokemon_data.special_defense,
                        speed=pokemon_data.speed,
                        nature=pokemon_data.nature,
                        ability=pokemon_data.ability,
                        is_shiny=pokemon_data.is_shiny,
                        rarity=pokemon_data.rarity,
                        gender=pokemon_data.gender,
                        nickname=pokemon_data.nickname,
                        in_team=pokemon_data.in_team,
                        team_position=pokemon_data.team_position,
                        created_at=pokemon_data.created_at
                    ))
                return pokemon_list
        except Exception as e:
            logger.error(f"Error getting Pokémon by species: {e}")
            return []
    
    async def get_shiny_pokemon(self, user_id: int) -> List[Pokemon]:
        """Get user's shiny Pokémon."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(SqlPokemon)
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.is_shiny == True)
                )
                pokemon_data_list = result.scalars().all()
                
                pokemon_list = []
                for pokemon_data in pokemon_data_list:
                    pokemon_list.append(Pokemon(
                        pokemon_id=pokemon_data.pokemon_id,
                        owner_id=pokemon_data.owner_id,
                        species=pokemon_data.species,
                        species_id=pokemon_data.species_id,
                        level=pokemon_data.level,
                        experience=pokemon_data.experience,
                        hp=pokemon_data.hp,
                        attack=pokemon_data.attack,
                        defense=pokemon_data.defense,
                        special_attack=pokemon_data.special_attack,
                        special_defense=pokemon_data.special_defense,
                        speed=pokemon_data.speed,
                        nature=pokemon_data.nature,
                        ability=pokemon_data.ability,
                        is_shiny=pokemon_data.is_shiny,
                        rarity=pokemon_data.rarity,
                        gender=pokemon_data.gender,
                        nickname=pokemon_data.nickname,
                        in_team=pokemon_data.in_team,
                        team_position=pokemon_data.team_position,
                        created_at=pokemon_data.created_at
                    ))
                return pokemon_list
        except Exception as e:
            logger.error(f"Error getting shiny Pokémon: {e}")
            return []
    
    async def get_pokemon_stats_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary statistics for user's Pokémon collection."""
        try:
            async with db.get_session() as session:
                # Get total count
                total_result = await session.execute(
                    select(func.count(SqlPokemon.id))
                    .where(SqlPokemon.owner_id == user_id)
                )
                total = total_result.scalar_one()
                
                if total == 0:
                    return {"total": 0, "shiny_count": 0, "average_level": 0, "highest_level": 0, "rarity_counts": {}}
                
                # Get shiny count
                shiny_result = await session.execute(
                    select(func.count(SqlPokemon.id))
                    .where(SqlPokemon.owner_id == user_id)
                    .where(SqlPokemon.is_shiny == True)
                )
                shiny_count = shiny_result.scalar_one()
                
                # Get level stats
                level_stats_result = await session.execute(
                    select(func.avg(SqlPokemon.level), func.max(SqlPokemon.level))
                    .where(SqlPokemon.owner_id == user_id)
                )
                avg_level, max_level = level_stats_result.one()
                
                # Get rarity counts
                rarity_result = await session.execute(
                    select(SqlPokemon.rarity, func.count(SqlPokemon.id))
                    .where(SqlPokemon.owner_id == user_id)
                    .group_by(SqlPokemon.rarity)
                )
                rarity_counts = dict(rarity_result.all())
                
                return {
                    "total": total,
                    "shiny_count": shiny_count,
                    "average_level": round(float(avg_level) if avg_level else 0, 1),
                    "highest_level": max_level or 0,
                    "rarity_counts": rarity_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting Pokémon stats summary: {e}")
            return {}


# Global service instance
pokemon_service = PokemonService()
