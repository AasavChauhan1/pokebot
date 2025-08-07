"""Fast scheduler service for automatic Pokemon spawning."""

import logging
import random
import asyncio
from datetime import datetime, timedelta
from typing import Set
from bot.services.spawn_service import spawn_service
from config.settings import settings
from config.database import db

logger = logging.getLogger(__name__)


class FastSchedulerService:
    """High-speed scheduler for automatic spawns."""
    
    def __init__(self):
        self.active_channels: Set[int] = set()
        self.running = False
        self.spawn_task = None
        
    def register_channel(self, chat_id: int) -> None:
        """Register a channel for auto-spawning."""
        self.active_channels.add(chat_id)
        logger.info(f"Registered channel {chat_id} for fast auto-spawning")
    
    def unregister_channel(self, chat_id: int) -> None:
        """Unregister a channel from auto-spawning."""
        self.active_channels.discard(chat_id)
        logger.info(f"Unregistered channel {chat_id} from auto-spawning")
    
    async def start_auto_spawning(self) -> None:
        """Start the fast auto-spawning system."""
        if self.running:
            return
            
        self.running = True
        self.spawn_task = asyncio.create_task(self._spawn_loop())
        logger.info("Fast auto-spawning started!")
    
    async def stop_auto_spawning(self) -> None:
        """Stop the auto-spawning system."""
        self.running = False
        if self.spawn_task:
            self.spawn_task.cancel()
            try:
                await self.spawn_task
            except asyncio.CancelledError:
                pass
        logger.info("Fast auto-spawning stopped")
    
    async def _spawn_loop(self) -> None:
        """Ultra-fast spawning loop with new service."""
        while self.running:
            try:
                if not self.active_channels:
                    await asyncio.sleep(5)
                    continue
                
                # Import here to avoid circular imports
                from bot.services.fast_spawn_service import fast_spawn_service
                
                # Fast random channel selection
                if self.active_channels:
                    channels_list = list(self.active_channels)
                    chat_id = random.choice(channels_list)
                    
                    # Quick spawn attempt
                    success = await fast_spawn_service.create_spawn(chat_id)
                    if success:
                        logger.info(f"Auto-spawned in channel {chat_id}")
                
                # Fast interval - spawns every 30-60 seconds
                interval = random.randint(30, 60)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Spawn loop error: {e}")
                await asyncio.sleep(10)
    
    async def force_spawn_all_channels(self) -> int:
        """Force spawn in all active channels - for testing."""
        spawned_count = 0
        for chat_id in self.active_channels:
            try:
                spawn = await spawn_service.create_spawn(chat_id)
                if spawn:
                    spawned_count += 1
            except Exception as e:
                logger.error(f"Error force spawning in {chat_id}: {e}")
        
        logger.info(f"Force spawned in {spawned_count} channels")
        return spawned_count
    
    async def cleanup_expired_spawns(self) -> None:
        """Fast cleanup of expired spawns."""
        try:
            async with db.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM spawns 
                    WHERE expires_at < $1 AND is_caught = FALSE
                """, datetime.utcnow())
                
                if result != "DELETE 0":
                    logger.info(f"Cleaned up expired spawns: {result}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up spawns: {e}")
    
    def get_stats(self) -> dict:
        """Get spawning statistics."""
        return {
            "active_channels": len(self.active_channels),
            "auto_spawning": self.running,
            "spawn_interval": f"{settings.AUTO_SPAWN_INTERVAL}s",
            "registered_channels": list(self.active_channels)
        }


# Global scheduler instance
scheduler_service = FastSchedulerService()
