"""User service for managing trainer data."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select, update, func
from bot.models.sql_models import User
from bot.utils.helpers import generate_id, get_level_from_exp, calculate_level_exp
from config.database import db

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user/trainer data."""
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            async with db.get_session() as session:
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
        """Create a new user."""
        try:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            
            async with db.get_session() as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                
            logger.info(f"Created new user: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            raise
    
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
        """Get existing user or create new one."""
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_user(user_id, username, first_name, last_name)
        return user
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user data."""
        try:
            async with db.get_session() as session:
                stmt = (
                    update(User)
                    .where(User.user_id == user_id)
                    .values(**update_data)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def add_experience(self, user_id: int, exp_amount: int) -> tuple[int, bool]:
        """Add experience to user and return new level and if leveled up."""
        user = await self.get_user(user_id)
        if not user:
            return 1, False
        
        old_level = user.trainer_level
        new_exp = user.experience + exp_amount
        new_level = get_level_from_exp(new_exp)
        
        leveled_up = new_level > old_level
        
        await self.update_user(user_id, {
            "experience": new_exp,
            "trainer_level": new_level
        })
        
        return new_level, leveled_up
    
    async def add_coins(self, user_id: int, amount: int) -> bool:
        """Add coins to user."""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        new_amount = max(0, user.coins + amount)
        return await self.update_user(user_id, {"coins": new_amount})
    
    async def spend_coins(self, user_id: int, amount: int) -> bool:
        """Spend coins if user has enough."""
        user = await self.get_user(user_id)
        if not user or user.coins < amount:
            return False
        
        return await self.add_coins(user_id, -amount)
    
    async def update_user_coins(self, user_id: int, new_amount: int) -> bool:
        """Update user's coin balance to a specific amount."""
        try:
            return await self.update_user(user_id, {"coins": max(0, new_amount)})
        except Exception as e:
            logger.error(f"Error updating coins for user {user_id}: {e}")
            return False
    
    async def claim_daily_reward(self, user_id: int) -> tuple[bool, Dict[str, Any]]:
        """Claim daily reward if available."""
        user = await self.get_user(user_id)
        if not user:
            return False, {}
        
        now = datetime.utcnow()
        last_claim = user.last_daily_claim
        
        # Check if already claimed today
        if last_claim and last_claim.date() == now.date():
            return False, {"error": "Already claimed today"}
        
        # Calculate streak
        streak = user.daily_streak
        if last_claim and (now - last_claim).days == 1:
            streak += 1
        elif not last_claim or (now - last_claim).days > 1:
            streak = 1
        
        # Calculate rewards based on streak
        base_coins = 100
        streak_bonus = min(streak * 10, 200)  # Max 200 bonus
        total_coins = base_coins + streak_bonus
        
        # Update user
        await self.update_user(user_id, {
            "daily_streak": streak,
            "last_daily_claim": now,
            "coins": user.coins + total_coins
        })
        
        reward = {
            "coins": total_coins,
            "streak": streak,
            "streak_bonus": streak_bonus
        }
        
        return True, reward
    
    async def get_leaderboard(self, category: str = "level", limit: int = 10) -> list:
        """Get leaderboard data."""
        try:
            sort_field = {
                "level": User.trainer_level,
                "pokemon": User.total_pokemon,
                "wins": User.battles_won,
                "coins": User.coins
            }.get(category, User.trainer_level)
            
            async with db.get_session() as session:
                result = await session.execute(
                    select(User.user_id, User.username, User.first_name, sort_field)
                    .order_by(sort_field.desc())
                    .limit(limit)
                )
                return [row._asdict() for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def update_battle_stats(self, user_id: int, won: bool) -> bool:
        """Update battle statistics."""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            update_data = {"battles_total": user.battles_total + 1}
            
            if won:
                update_data["battles_won"] = user.battles_won + 1
            else:
                update_data["battles_lost"] = user.battles_lost + 1
            
            return await self.update_user(user_id, update_data)
        except Exception as e:
            logger.error(f"Error updating battle stats for {user_id}: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive user statistics."""
        user = await self.get_user(user_id)
        if not user:
            return None
        
        try:
            # Get additional stats from pokemon table
            from bot.models.sql_models import Pokemon
            
            async with db.get_session() as session:
                # Count total pokemon
                pokemon_count_result = await session.execute(
                    select(func.count(Pokemon.id)).where(Pokemon.owner_id == user_id)
                )
                pokemon_count = pokemon_count_result.scalar()
                
                # Count shiny pokemon
                shiny_count_result = await session.execute(
                    select(func.count(Pokemon.id)).where(
                        Pokemon.owner_id == user_id,
                        Pokemon.is_shiny == True
                    )
                )
                shiny_count = shiny_count_result.scalar()
            
            return {
                "user": user,
                "pokemon_count": pokemon_count,
                "shiny_count": shiny_count,
                "win_rate": user.battles_won / max(user.battles_total, 1) * 100,
                "next_level_exp": calculate_level_exp(user.trainer_level + 1) - user.experience
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {
                "user": user,
                "pokemon_count": 0,
                "shiny_count": 0,
                "win_rate": 0,
                "next_level_exp": calculate_level_exp(user.trainer_level + 1) - user.experience
            }


# Global service instance
user_service = UserService()
