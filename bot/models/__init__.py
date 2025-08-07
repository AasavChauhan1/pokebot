"""Data models for the Pokémon bot."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PokemonRarity(str, Enum):
    """Pokémon rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class BattleStatus(str, Enum):
    """Battle status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TradeStatus(str, Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ItemType(str, Enum):
    """Item type enumeration."""
    POKEBALL = "pokeball"
    POTION = "potion"
    BERRY = "berry"
    EVOLUTION_STONE = "evolution_stone"
    HELD_ITEM = "held_item"
    KEY_ITEM = "key_item"


class User(BaseModel):
    """User/Trainer model."""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Trainer stats
    trainer_level: int = 1
    experience: int = 0
    coins: int = 1000
    
    # Pokémon collection
    total_pokemon: int = 0
    pokemon_caught: int = 0
    pokemon_seen: int = 0
    
    # Battle stats
    battles_won: int = 0
    battles_lost: int = 0
    battles_total: int = 0
    
    # Daily/streak stats
    daily_streak: int = 0
    last_daily_claim: Optional[datetime] = None
    last_spawn_claim: Optional[datetime] = None
    
    # Settings
    language: str = "en"
    notifications_enabled: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class Pokemon(BaseModel):
    """Pokémon model."""
    pokemon_id: str  # Unique identifier
    owner_id: int
    
    # Basic info
    species: str  # Pokémon name (e.g., "pikachu")
    species_id: int  # PokeAPI species ID
    nickname: Optional[str] = None
    
    # Stats
    level: int = 1
    experience: int = 0
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    # Attributes
    nature: str
    ability: str
    gender: Optional[str] = None
    is_shiny: bool = False
    rarity: PokemonRarity = PokemonRarity.COMMON
    
    # Game mechanics
    in_team: bool = False
    team_position: Optional[int] = None
    held_item: Optional[str] = None
    
    # Breeding/Evolution
    can_evolve: bool = False
    evolution_stage: int = 1
    
    # Timestamps
    caught_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class InventoryItem(BaseModel):
    """Inventory item model."""
    item_id: str
    name: str
    item_type: ItemType
    quantity: int = 1
    description: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class Battle(BaseModel):
    """Battle model."""
    battle_id: str
    challenger_id: int
    defender_id: Optional[int] = None  # None for AI battles
    
    # Battle configuration
    battle_type: str = "pve"  # "pvp" or "pve"
    status: BattleStatus = BattleStatus.PENDING
    
    # Teams
    challenger_team: List[str] = []  # Pokemon IDs
    defender_team: List[str] = []    # Pokemon IDs
    
    # Battle state
    current_turn: int = 0
    challenger_current_pokemon: Optional[int] = None
    defender_current_pokemon: Optional[int] = None
    
    # Results
    winner_id: Optional[int] = None
    experience_gained: Dict[str, int] = {}  # pokemon_id -> exp
    rewards: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class Trade(BaseModel):
    """Trade model."""
    trade_id: str
    initiator_id: int
    target_id: int
    
    # Trade items
    initiator_pokemon: List[str] = []  # Pokemon IDs
    initiator_items: Dict[str, int] = {}  # item_id -> quantity
    initiator_coins: int = 0
    
    target_pokemon: List[str] = []  # Pokemon IDs
    target_items: Dict[str, int] = {}  # item_id -> quantity
    target_coins: int = 0
    
    # Trade state
    status: TradeStatus = TradeStatus.PENDING
    initiator_confirmed: bool = False
    target_confirmed: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class Spawn(BaseModel):
    """Pokémon spawn model."""
    spawn_id: str
    chat_id: int
    message_id: Optional[int] = None
    
    # Spawned Pokémon
    species: str
    species_id: int
    level: int
    is_shiny: bool = False
    rarity: PokemonRarity = PokemonRarity.COMMON
    
    # Spawn state
    is_caught: bool = False
    caught_by: Optional[int] = None
    caught_at: Optional[datetime] = None
    
    # Timestamps
    spawned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class Quest(BaseModel):
    """Quest/Mission model."""
    quest_id: str
    user_id: int
    
    # Quest details
    quest_type: str  # "daily", "weekly", "monthly", "special"
    title: str
    description: str
    
    # Requirements
    target_type: str  # "catch", "battle", "evolve", etc.
    target_count: int
    current_count: int = 0
    
    # Rewards
    reward_coins: int = 0
    reward_items: Dict[str, int] = {}
    reward_exp: int = 0
    
    # Status
    is_completed: bool = False
    is_claimed: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
