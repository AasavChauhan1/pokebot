"""Configuration settings for the Pokémon bot."""

from typing import List
from decouple import config


class Settings:
    """Application settings loaded from environment variables."""
    
    # Bot Configuration
    BOT_TOKEN: str = config('BOT_TOKEN')
    DEBUG: bool = config('DEBUG', default=False, cast=bool)
    LOG_LEVEL: str = config('LOG_LEVEL', default='INFO')
    
    # Database Configuration
    DATABASE_URL: str = config('DATABASE_URL')
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Get async-compatible database URL."""
        import urllib.parse
        
        # Parse the URL  
        parsed = urllib.parse.urlparse(self.DATABASE_URL)
        
        # For SQLAlchemy with asyncpg, remove all query parameters that cause issues
        # asyncpg handles SSL differently
        clean_url = urllib.parse.urlunparse((
            'postgresql+asyncpg',
            parsed.netloc, 
            parsed.path,
            parsed.params,
            '',  # No query parameters
            parsed.fragment
        ))
        
        return clean_url
    
    @property
    def ASYNCPG_DATABASE_URL(self) -> str:
        """Get asyncpg-compatible database URL."""
        import urllib.parse
        
        # Parse the URL
        parsed = urllib.parse.urlparse(self.DATABASE_URL)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        # Keep only SSL mode, remove channel_binding
        clean_params = {}
        if 'sslmode' in query_params:
            clean_params['sslmode'] = query_params['sslmode'][0]
        
        # Reconstruct URL
        new_query = urllib.parse.urlencode(clean_params)
        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc, 
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return clean_url
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [
        int(admin_id.strip()) 
        for admin_id in config('ADMIN_IDS', default='').split(',') 
        if admin_id.strip()
    ]
    
    # External APIs
    POKEAPI_BASE_URL: str = config('POKEAPI_BASE_URL', default='https://pokeapi.co/api/v2')
    
    # Game Settings - Optimized for speed
    SPAWN_COOLDOWN: int = config('SPAWN_COOLDOWN', default=30, cast=int)  # 30 seconds - much faster!
    AUTO_SPAWN_INTERVAL: int = config('AUTO_SPAWN_INTERVAL', default=45, cast=int)  # Auto spawn every 45 seconds
    SPAWN_EXPIRY_TIME: int = config('SPAWN_EXPIRY_TIME', default=300, cast=int)  # 5 minutes to catch
    DAILY_REWARD_RESET_HOUR: int = config('DAILY_REWARD_RESET_HOUR', default=0, cast=int)
    MAX_POKEMON_PER_USER: int = config('MAX_POKEMON_PER_USER', default=1000, cast=int)
    MAX_INVENTORY_ITEMS: int = config('MAX_INVENTORY_ITEMS', default=500, cast=int)
    
    # Spawn chance settings
    SHINY_CHANCE: float = config('SHINY_CHANCE', default=0.005, cast=float)  # 0.5% chance - higher for fun
    AUTO_SPAWN_ENABLED: bool = config('AUTO_SPAWN_ENABLED', default=True, cast=bool)
    
    # Battle Settings
    BATTLE_TIMEOUT: int = config('BATTLE_TIMEOUT', default=300, cast=int)  # 5 minutes
    MAX_TEAM_SIZE: int = config('MAX_TEAM_SIZE', default=6, cast=int)
    
    # Economy Settings
    STARTING_COINS: int = config('STARTING_COINS', default=1000, cast=int)
    DAILY_COINS_REWARD: int = config('DAILY_COINS_REWARD', default=100, cast=int)
    
    def __init__(self):
        """Validate required settings."""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")


# Global settings instance
settings = Settings()
