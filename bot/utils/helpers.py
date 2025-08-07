"""Utility functions for the Pokémon bot."""

import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bot.models import PokemonRarity


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}{timestamp}{random_part}" if prefix else f"{timestamp}{random_part}"


def calculate_level_exp(level: int) -> int:
    """Calculate total experience needed for a given level."""
    if level <= 1:
        return 0
    # Using a polynomial formula similar to Pokémon games
    return int(level ** 3)


def calculate_exp_for_next_level(current_level: int) -> int:
    """Calculate experience needed to reach the next level."""
    return calculate_level_exp(current_level + 1) - calculate_level_exp(current_level)


def get_level_from_exp(experience: int) -> int:
    """Calculate level based on total experience."""
    if experience <= 0:
        return 1
    
    level = 1
    while calculate_level_exp(level + 1) <= experience:
        level += 1
    
    return min(level, 100)  # Cap at level 100


def calculate_pokemon_stats(base_stats: Dict[str, int], level: int, nature: str = "hardy") -> Dict[str, int]:
    """Calculate Pokémon stats based on base stats, level, and nature."""
    # Simplified stat calculation (not as complex as actual Pokémon games)
    stats = {}
    
    for stat_name, base_value in base_stats.items():
        if stat_name == 'hp':
            # HP calculation
            stats[stat_name] = int(((2 * base_value + 31) * level / 100) + level + 10)
        else:
            # Other stats calculation
            stat_value = int(((2 * base_value + 31) * level / 100) + 5)
            
            # Apply nature modifier (simplified)
            nature_modifiers = get_nature_modifiers(nature)
            if stat_name in nature_modifiers:
                stat_value = int(stat_value * nature_modifiers[stat_name])
            
            stats[stat_name] = stat_value
    
    return stats


def get_nature_modifiers(nature: str) -> Dict[str, float]:
    """Get stat modifiers for a given nature."""
    natures = {
        "hardy": {},  # No modifiers
        "adamant": {"attack": 1.1, "special_attack": 0.9},
        "modest": {"special_attack": 1.1, "attack": 0.9},
        "timid": {"speed": 1.1, "attack": 0.9},
        "jolly": {"speed": 1.1, "special_attack": 0.9},
        "bold": {"defense": 1.1, "attack": 0.9},
        "calm": {"special_defense": 1.1, "attack": 0.9},
    }
    return natures.get(nature, {})


def get_random_nature() -> str:
    """Get a random nature."""
    natures = ["hardy", "adamant", "modest", "timid", "jolly", "bold", "calm"]
    return random.choice(natures)


def determine_rarity(pokemon_id: int, is_shiny: bool = False) -> PokemonRarity:
    """Determine Pokémon rarity based on species and shiny status."""
    if is_shiny:
        # Shiny Pokémon are always at least rare
        if pokemon_id in get_legendary_pokemon():
            return PokemonRarity.MYTHICAL
        elif pokemon_id in get_rare_pokemon():
            return PokemonRarity.LEGENDARY
        else:
            return PokemonRarity.EPIC
    
    # Legendary Pokémon
    if pokemon_id in get_legendary_pokemon():
        return PokemonRarity.LEGENDARY
    
    # Rare Pokémon (pseudo-legendaries, etc.)
    if pokemon_id in get_rare_pokemon():
        return PokemonRarity.RARE
    
    # Uncommon Pokémon (starters, evolved forms)
    if pokemon_id in get_uncommon_pokemon():
        return PokemonRarity.UNCOMMON
    
    return PokemonRarity.COMMON


def get_legendary_pokemon() -> List[int]:
    """Get list of legendary Pokémon IDs."""
    return [
        144, 145, 146, 150, 151,  # Gen 1
        243, 244, 245, 249, 250, 251,  # Gen 2
        377, 378, 379, 380, 381, 382, 383, 384, 385, 386,  # Gen 3
        480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493,  # Gen 4
        494, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649,  # Gen 5
    ]


def get_rare_pokemon() -> List[int]:
    """Get list of rare Pokémon IDs (pseudo-legendaries, etc.)."""
    return [
        149,  # Dragonite line
        248,  # Tyranitar line
        376,  # Metagross line
        445,  # Garchomp line
        600,  # Hydreigon line
    ]


def get_uncommon_pokemon() -> List[int]:
    """Get list of uncommon Pokémon IDs (starters, evolved forms)."""
    starters = [
        1, 4, 7,    # Gen 1 starters
        152, 155, 158,  # Gen 2 starters
        252, 255, 258,  # Gen 3 starters
        387, 390, 393,  # Gen 4 starters
        495, 498, 501,  # Gen 5 starters
    ]
    return starters


def calculate_shiny_chance() -> bool:
    """Calculate if a Pokémon should be shiny (1/4096 chance)."""
    return random.randint(1, 4096) == 1


def format_time_delta(delta: timedelta) -> str:
    """Format a timedelta to a human-readable string."""
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def get_type_effectiveness(attacking_type: str, defending_type: str) -> float:
    """Get type effectiveness multiplier."""
    # Simplified type chart (not complete)
    effectiveness = {
        "fire": {"grass": 2.0, "water": 0.5, "fire": 0.5},
        "water": {"fire": 2.0, "grass": 0.5, "water": 0.5},
        "grass": {"water": 2.0, "fire": 0.5, "grass": 0.5},
        "electric": {"water": 2.0, "grass": 0.5, "electric": 0.5, "ground": 0.0},
        "ground": {"electric": 2.0, "grass": 0.5, "flying": 0.0},
        "flying": {"grass": 2.0, "electric": 2.0, "ground": 0.0},
    }
    
    return effectiveness.get(attacking_type, {}).get(defending_type, 1.0)


def generate_battle_damage(attacker_attack: int, defender_defense: int, move_power: int = 80, type_effectiveness: float = 1.0) -> int:
    """Calculate battle damage."""
    # Simplified damage calculation
    base_damage = ((attacker_attack * move_power) / defender_defense) * 0.4
    damage = int(base_damage * type_effectiveness * random.uniform(0.85, 1.0))
    return max(1, damage)  # Minimum 1 damage


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def format_pokemon_name(name: str, nickname: Optional[str] = None, is_shiny: bool = False) -> str:
    """Format a Pokémon name for display."""
    display_name = nickname if nickname else name.title()
    if is_shiny:
        return f"✨ {display_name}"
    return display_name


def format_coins(amount: int) -> str:
    """Format coin amount for display."""
    if amount >= 1000000:
        return f"{amount / 1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount / 1000:.1f}K"
    else:
        return str(amount)


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    from config.settings import settings
    return user_id in settings.ADMIN_IDS


def get_rarity_emoji(rarity: PokemonRarity) -> str:
    """Get emoji for rarity level."""
    rarity_emojis = {
        PokemonRarity.COMMON: "⚪",
        PokemonRarity.UNCOMMON: "🟢",
        PokemonRarity.RARE: "🔵",
        PokemonRarity.EPIC: "🟣",
        PokemonRarity.LEGENDARY: "🟡",
        PokemonRarity.MYTHICAL: "🔴",
    }
    return rarity_emojis.get(rarity, "⚪")


def get_type_emoji(pokemon_type: str) -> str:
    """Get emoji for Pokémon type."""
    type_emojis = {
        "normal": "⚪",
        "fire": "🔥",
        "water": "💧",
        "electric": "⚡",
        "grass": "🌿",
        "ice": "❄️",
        "fighting": "👊",
        "poison": "☠️",
        "ground": "🌍",
        "flying": "🌪️",
        "psychic": "🔮",
        "bug": "🐛",
        "rock": "🪨",
        "ghost": "👻",
        "dragon": "🐉",
        "dark": "🌑",
        "steel": "⚙️",
        "fairy": "🧚",
    }
    return type_emojis.get(pokemon_type, "❓")
