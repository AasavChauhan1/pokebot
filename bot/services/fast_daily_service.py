"""Ultra-fast daily rewards service with pure SQL operations."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncpg

from config.database import db

logger = logging.getLogger(__name__)


class RawSQLDailyService:
    """Raw SQL daily service for maximum speed."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_user_daily_status(self, user_id: int) -> Dict:
        """Get user's daily claim status."""
        try:
            async with db.pool.acquire() as conn:
                # Direct SQL query for user daily data
                row = await conn.fetchrow("""
                    SELECT user_id, daily_streak, last_daily_claim, coins
                    FROM users 
                    WHERE user_id = $1
                """, user_id)
                
                if not row:
                    return {
                        "exists": False,
                        "can_claim": True,
                        "streak": 0,
                        "coins": 0,
                        "hours_left": 0
                    }
                
                last_claim = row['last_daily_claim']
                now = datetime.utcnow()
                
                if not last_claim:
                    return {
                        "exists": True,
                        "can_claim": True,
                        "streak": row['daily_streak'] or 0,
                        "coins": row['coins'] or 0,
                        "hours_left": 0
                    }
                
                time_diff = now - last_claim
                can_claim = time_diff.total_seconds() >= 18000  # 5 hours
                hours_left = max(0, 5 - int(time_diff.total_seconds() / 3600))
                
                return {
                    "exists": True,
                    "can_claim": can_claim,
                    "streak": row['daily_streak'] or 0,
                    "coins": row['coins'] or 0,
                    "hours_left": hours_left,
                    "last_claim": last_claim
                }
                
        except Exception as e:
            self.logger.error(f"Error getting daily status: {e}")
            return {
                "exists": False,
                "can_claim": True,
                "streak": 0,
                "coins": 0,
                "hours_left": 0
            }
    
    async def create_new_user(self, user_id: int, username: str, first_name: str, last_name: str = None) -> bool:
        """Create new user with welcome bonus."""
        try:
            async with db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name, coins, daily_streak, last_daily_claim)
                    VALUES ($1, $2, $3, $4, 1100, 1, $5)
                    ON CONFLICT (user_id) DO NOTHING
                """, user_id, username or "trainer", first_name or "Unknown", last_name, datetime.utcnow())
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False
    
    async def claim_daily_reward(self, user_id: int) -> Dict:
        """Claim daily reward and calculate streak."""
        try:
            status = await self.get_user_daily_status(user_id)
            
            if not status["can_claim"]:
                return {
                    "success": False,
                    "reason": "already_claimed",
                    "hours_left": status["hours_left"],
                    "streak": status["streak"],
                    "coins": status["coins"]
                }
            
            now = datetime.utcnow()
            
            # Calculate new streak
            if status["exists"] and "last_claim" in status and status["last_claim"]:
                time_since_last = now - status["last_claim"]
                if time_since_last.total_seconds() <= 129600:  # 36 hours grace period
                    new_streak = status["streak"] + 1
                else:
                    new_streak = 1  # Reset streak
            else:
                new_streak = 1
            
            # Calculate rewards
            base_reward = 100
            streak_bonus = min(new_streak * 20, 500)  # Max 500 bonus
            total_reward = base_reward + streak_bonus
            
            # Update user with new rewards
            async with db.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET coins = coins + $2, daily_streak = $3, last_daily_claim = $4
                    WHERE user_id = $1
                """, user_id, total_reward, new_streak, now)
            
            return {
                "success": True,
                "base_reward": base_reward,
                "streak_bonus": streak_bonus,
                "total_reward": total_reward,
                "new_streak": new_streak,
                "is_milestone": new_streak in [7, 14, 30]
            }
            
        except Exception as e:
            self.logger.error(f"Error claiming daily reward: {e}")
            return {
                "success": False,
                "reason": "error",
                "error": str(e)
            }


# Global instance
fast_daily_service = RawSQLDailyService()
