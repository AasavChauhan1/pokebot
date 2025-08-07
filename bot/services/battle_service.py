"""Simple battle system for Pokémon battles."""

import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from bot.models import Pokemon, Battle, BattleStatus
from bot.services.pokemon_service import pokemon_service
from bot.services.user_service import user_service
from bot.utils.helpers import generate_id, get_type_effectiveness, generate_battle_damage
from config.database import db

logger = logging.getLogger(__name__)


class BattleService:
    """Service for managing battles between Pokémon."""
    
    async def create_battle(self, challenger_id: int, defender_id: Optional[int] = None, battle_type: str = "pve") -> Optional[Battle]:
        """Create a new battle."""
        try:
            battle = Battle(
                battle_id=generate_id("battle_"),
                challenger_id=challenger_id,
                defender_id=defender_id,
                battle_type=battle_type,
                status=BattleStatus.PENDING
            )
            
            await db.db.battles.insert_one(battle.dict())
            logger.info(f"Created battle {battle.battle_id} between {challenger_id} and {defender_id}")
            
            return battle
            
        except Exception as e:
            logger.error(f"Error creating battle: {e}")
            return None
    
    async def get_battle(self, battle_id: str) -> Optional[Battle]:
        """Get battle by ID."""
        try:
            battle_data = await db.db.battles.find_one({"battle_id": battle_id})
            if battle_data:
                return Battle(**battle_data)
            return None
        except Exception as e:
            logger.error(f"Error getting battle {battle_id}: {e}")
            return None
    
    async def start_battle(self, battle_id: str, challenger_team: List[str], defender_team: List[str] = None) -> bool:
        """Start a battle with selected teams."""
        try:
            battle = await self.get_battle(battle_id)
            if not battle or battle.status != BattleStatus.PENDING:
                return False
            
            # For PvE battles, generate AI team
            if battle.battle_type == "pve" and not defender_team:
                defender_team = await self._generate_ai_team(challenger_team)
            
            # Update battle with teams
            update_data = {
                "challenger_team": challenger_team,
                "defender_team": defender_team or [],
                "status": BattleStatus.ACTIVE,
                "started_at": datetime.utcnow(),
                "challenger_current_pokemon": 0,
                "defender_current_pokemon": 0
            }
            
            result = await db.db.battles.update_one(
                {"battle_id": battle_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error starting battle: {e}")
            return False
    
    async def execute_turn(self, battle_id: str, attacker_id: int, move: str = "tackle") -> Dict[str, any]:
        """Execute a battle turn."""
        try:
            battle = await self.get_battle(battle_id)
            if not battle or battle.status != BattleStatus.ACTIVE:
                return {"error": "Battle not active"}
            
            # Determine attacker and defender
            is_challenger = attacker_id == battle.challenger_id
            
            if is_challenger:
                attacker_pokemon_idx = battle.challenger_current_pokemon
                defender_pokemon_idx = battle.defender_current_pokemon
                attacker_team = battle.challenger_team
                defender_team = battle.defender_team
            else:
                attacker_pokemon_idx = battle.defender_current_pokemon
                defender_pokemon_idx = battle.challenger_current_pokemon
                attacker_team = battle.defender_team
                defender_team = battle.challenger_team
            
            # Get current Pokémon
            attacker_pokemon = await pokemon_service.get_pokemon(attacker_team[attacker_pokemon_idx])
            defender_pokemon = await pokemon_service.get_pokemon(defender_team[defender_pokemon_idx])
            
            if not attacker_pokemon or not defender_pokemon:
                return {"error": "Pokémon not found"}
            
            # Calculate damage
            damage = generate_battle_damage(
                attacker_pokemon.attack,
                defender_pokemon.defense,
                move_power=80,  # Default move power
                type_effectiveness=1.0  # Simplified for now
            )
            
            # Apply damage
            new_hp = max(0, defender_pokemon.hp - damage)
            
            # Update defender's HP
            await db.db.pokemon.update_one(
                {"pokemon_id": defender_pokemon.pokemon_id},
                {"$set": {"hp": new_hp}}
            )
            
            # Check if Pokémon fainted
            fainted = new_hp <= 0
            battle_ended = False
            winner_id = None
            
            if fainted:
                # Switch to next Pokémon or end battle
                next_pokemon_idx = defender_pokemon_idx + 1
                
                if is_challenger:
                    if next_pokemon_idx >= len(defender_team):
                        # Challenger wins
                        battle_ended = True
                        winner_id = battle.challenger_id
                    else:
                        await db.db.battles.update_one(
                            {"battle_id": battle_id},
                            {"$set": {"defender_current_pokemon": next_pokemon_idx}}
                        )
                else:
                    if next_pokemon_idx >= len(attacker_team):
                        # Defender wins
                        battle_ended = True
                        winner_id = battle.defender_id or -1  # AI wins
                    else:
                        await db.db.battles.update_one(
                            {"battle_id": battle_id},
                            {"$set": {"challenger_current_pokemon": next_pokemon_idx}}
                        )
            
            # End battle if needed
            if battle_ended:
                await self._end_battle(battle_id, winner_id)
            
            # Increment turn
            await db.db.battles.update_one(
                {"battle_id": battle_id},
                {"$inc": {"current_turn": 1}}
            )
            
            return {
                "success": True,
                "damage": damage,
                "defender_hp": new_hp,
                "fainted": fainted,
                "battle_ended": battle_ended,
                "winner_id": winner_id
            }
            
        except Exception as e:
            logger.error(f"Error executing battle turn: {e}")
            return {"error": "Turn execution failed"}
    
    async def _end_battle(self, battle_id: str, winner_id: Optional[int]) -> None:
        """End a battle and distribute rewards."""
        try:
            battle = await self.get_battle(battle_id)
            if not battle:
                return
            
            # Calculate experience rewards
            exp_rewards = {}
            
            # Give experience to all participating Pokémon
            for pokemon_id in battle.challenger_team:
                exp_rewards[pokemon_id] = 50  # Base experience
            
            for pokemon_id in battle.defender_team:
                exp_rewards[pokemon_id] = 30  # Less for defender
            
            # Bonus experience for winner
            if winner_id:
                winning_team = battle.challenger_team if winner_id == battle.challenger_id else battle.defender_team
                for pokemon_id in winning_team:
                    exp_rewards[pokemon_id] = exp_rewards.get(pokemon_id, 0) + 25
            
            # Apply experience rewards
            for pokemon_id, exp in exp_rewards.items():
                await pokemon_service.give_experience(pokemon_id, exp)
            
            # Update user battle stats
            if winner_id == battle.challenger_id:
                await user_service.update_battle_stats(battle.challenger_id, won=True)
                if battle.defender_id:
                    await user_service.update_battle_stats(battle.defender_id, won=False)
            elif winner_id == battle.defender_id:
                await user_service.update_battle_stats(battle.challenger_id, won=False)
                await user_service.update_battle_stats(battle.defender_id, won=True)
            
            # Give coin rewards
            if winner_id in [battle.challenger_id, battle.defender_id]:
                coin_reward = 100 + (len(battle.challenger_team) * 10)
                await user_service.add_coins(winner_id, coin_reward)
            
            # Update battle status
            await db.db.battles.update_one(
                {"battle_id": battle_id},
                {"$set": {
                    "status": BattleStatus.COMPLETED,
                    "ended_at": datetime.utcnow(),
                    "winner_id": winner_id,
                    "experience_gained": exp_rewards,
                    "rewards": {"coins": coin_reward if winner_id else 0}
                }}
            )
            
        except Exception as e:
            logger.error(f"Error ending battle: {e}")
    
    async def _generate_ai_team(self, challenger_team: List[str]) -> List[str]:
        """Generate an AI team for PvE battles."""
        try:
            # Get challenger team average level
            total_level = 0
            team_count = 0
            
            for pokemon_id in challenger_team:
                pokemon = await pokemon_service.get_pokemon(pokemon_id)
                if pokemon:
                    total_level += pokemon.level
                    team_count += 1
            
            avg_level = total_level // max(team_count, 1)
            
            # Generate AI Pokémon at similar level
            ai_team = []
            for i in range(min(len(challenger_team), 3)):  # AI uses up to 3 Pokémon
                # Random Pokémon ID
                species_id = random.randint(1, 151)  # Gen 1 for simplicity
                
                # Create temporary AI Pokémon
                ai_pokemon = await pokemon_service.create_pokemon(
                    owner_id=-1,  # Special AI owner ID
                    species_id=species_id,
                    level=max(1, avg_level + random.randint(-5, 5))
                )
                
                if ai_pokemon:
                    ai_team.append(ai_pokemon.pokemon_id)
            
            return ai_team
            
        except Exception as e:
            logger.error(f"Error generating AI team: {e}")
            return []
    
    async def get_user_active_battle(self, user_id: int) -> Optional[Battle]:
        """Get user's active battle."""
        try:
            battle_data = await db.db.battles.find_one({
                "$or": [
                    {"challenger_id": user_id},
                    {"defender_id": user_id}
                ],
                "status": BattleStatus.ACTIVE
            })
            
            if battle_data:
                return Battle(**battle_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting active battle: {e}")
            return None
    
    async def forfeit_battle(self, battle_id: str, user_id: int) -> bool:
        """Forfeit a battle."""
        try:
            battle = await self.get_battle(battle_id)
            if not battle or battle.status != BattleStatus.ACTIVE:
                return False
            
            if user_id not in [battle.challenger_id, battle.defender_id]:
                return False
            
            # Determine winner (the other player)
            winner_id = battle.defender_id if user_id == battle.challenger_id else battle.challenger_id
            
            await self._end_battle(battle_id, winner_id)
            return True
            
        except Exception as e:
            logger.error(f"Error forfeiting battle: {e}")
            return False


# Global service instance
battle_service = BattleService()
