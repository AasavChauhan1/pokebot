"""PokeAPI service for fetching Pokémon data."""

import logging
import asyncio
from typing import Optional, Dict, Any, List
import aiohttp
from config.settings import settings

logger = logging.getLogger(__name__)


class PokeAPIService:
    """Service for interacting with the PokeAPI."""
    
    def __init__(self):
        self.base_url = settings.POKEAPI_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Any] = {}
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Fetch data from PokeAPI with caching."""
        cache_key = f"pokeapi:{endpoint}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            session = await self._get_session()
            url = f"{self.base_url}/{endpoint}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self._cache[cache_key] = data
                    return data
                else:
                    logger.error(f"PokeAPI request failed: {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching from PokeAPI: {e}")
            return None
    
    async def get_pokemon_species(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Get Pokémon species data."""
        return await self._fetch_data(f"pokemon-species/{pokemon_id}")
    
    async def get_pokemon_data(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Get Pokémon data including stats."""
        return await self._fetch_data(f"pokemon/{pokemon_id}")
    
    async def get_evolution_chain(self, chain_id: int) -> Optional[Dict[str, Any]]:
        """Get evolution chain data."""
        return await self._fetch_data(f"evolution-chain/{chain_id}")
    
    async def get_random_pokemon_id(self) -> int:
        """Get a random Pokémon ID (1-1010 for all generations)."""
        import random
        return random.randint(1, 1010)
    
    async def get_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get Pokémon data by name."""
        return await self._fetch_data(f"pokemon/{name.lower()}")
    
    async def get_pokemon_stats(self, pokemon_id: int) -> Dict[str, int]:
        """Get base stats for a Pokémon."""
        data = await self.get_pokemon_data(pokemon_id)
        if not data:
            return {}
        
        stats = {}
        for stat_data in data.get('stats', []):
            stat_name = stat_data['stat']['name']
            base_stat = stat_data['base_stat']
            
            # Map stat names to our model
            if stat_name == 'hp':
                stats['hp'] = base_stat
            elif stat_name == 'attack':
                stats['attack'] = base_stat
            elif stat_name == 'defense':
                stats['defense'] = base_stat
            elif stat_name == 'special-attack':
                stats['special_attack'] = base_stat
            elif stat_name == 'special-defense':
                stats['special_defense'] = base_stat
            elif stat_name == 'speed':
                stats['speed'] = base_stat
        
        return stats
    
    async def get_pokemon_abilities(self, pokemon_id: int) -> List[str]:
        """Get list of abilities for a Pokémon."""
        data = await self.get_pokemon_data(pokemon_id)
        if not data:
            return []
        
        abilities = []
        for ability_data in data.get('abilities', []):
            abilities.append(ability_data['ability']['name'])
        
        return abilities
    
    async def get_pokemon_types(self, pokemon_id: int) -> List[str]:
        """Get types for a Pokémon."""
        data = await self.get_pokemon_data(pokemon_id)
        if not data:
            return []
        
        types = []
        for type_data in data.get('types', []):
            types.append(type_data['type']['name'])
        
        return types
    
    async def get_pokemon_sprite_url(self, pokemon_id: int, shiny: bool = False) -> Optional[str]:
        """Get sprite URL for a Pokémon."""
        data = await self.get_pokemon_data(pokemon_id)
        if not data:
            return None
        
        sprites = data.get('sprites', {})
        if shiny:
            return sprites.get('front_shiny') or sprites.get('front_default')
        else:
            return sprites.get('front_default')
    
    async def get_pokemon_name(self, pokemon_id: int) -> str:
        """Get the display name of a Pokémon."""
        data = await self.get_pokemon_data(pokemon_id)
        if data:
            return data.get('name', f'pokemon-{pokemon_id}').title()
        return f'Pokemon #{pokemon_id}'
    
    async def search_pokemon(self, query: str) -> List[Dict[str, Any]]:
        """Search for Pokémon by name (simplified)."""
        # For a more robust search, you'd want to fetch a list of all Pokémon
        # and implement fuzzy matching. For now, just try exact match.
        try:
            data = await self.get_pokemon_by_name(query)
            if data:
                return [data]
            return []
        except:
            return []


# Global service instance
pokeapi = PokeAPIService()
