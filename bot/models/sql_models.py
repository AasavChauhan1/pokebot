"""SQLAlchemy models for PostgreSQL database."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float, 
    BigInteger, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class PokemonRarity(str, enum.Enum):
    """Pokémon rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"


class BattleStatus(str, enum.Enum):
    """Battle status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TradeStatus(str, enum.Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """User/Trainer table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Trainer stats
    trainer_level = Column(Integer, default=1, nullable=False, index=True)
    experience = Column(BigInteger, default=0, nullable=False)
    coins = Column(BigInteger, default=1000, nullable=False)
    
    # Pokémon collection
    total_pokemon = Column(Integer, default=0, nullable=False, index=True)
    pokemon_caught = Column(Integer, default=0, nullable=False)
    pokemon_seen = Column(Integer, default=0, nullable=False)
    
    # Battle stats
    battles_won = Column(Integer, default=0, nullable=False)
    battles_lost = Column(Integer, default=0, nullable=False)
    battles_total = Column(Integer, default=0, nullable=False)
    
    # Daily/streak stats
    daily_streak = Column(Integer, default=0, nullable=False)
    last_daily_claim = Column(DateTime, nullable=True)
    last_spawn_claim = Column(DateTime, nullable=True)
    
    # Settings
    language = Column(String(10), default="en", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Pokemon(Base):
    """Pokémon table."""
    __tablename__ = "pokemon"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pokemon_id = Column(String(255), unique=True, nullable=False, index=True)
    owner_id = Column(BigInteger, nullable=False, index=True)
    
    # Basic info
    species = Column(String(255), nullable=False, index=True)
    species_id = Column(Integer, nullable=False)
    nickname = Column(String(255), nullable=True)
    
    # Stats
    level = Column(Integer, default=1, nullable=False)
    experience = Column(BigInteger, default=0, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    special_attack = Column(Integer, nullable=False)
    special_defense = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    
    # Attributes
    nature = Column(String(50), nullable=False)
    ability = Column(String(255), nullable=False)
    gender = Column(String(10), nullable=True)
    is_shiny = Column(Boolean, default=False, nullable=False, index=True)
    rarity = Column(SQLEnum(PokemonRarity), default=PokemonRarity.COMMON, nullable=False, index=True)
    
    # Game mechanics
    in_team = Column(Boolean, default=False, nullable=False)
    team_position = Column(Integer, nullable=True)
    held_item = Column(String(255), nullable=True)
    
    # Breeding/Evolution
    can_evolve = Column(Boolean, default=False, nullable=False)
    evolution_stage = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    caught_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_owner_team', 'owner_id', 'in_team'),
        Index('idx_species_rarity', 'species', 'rarity'),
    )


class Spawn(Base):
    """Pokémon spawn table."""
    __tablename__ = "spawns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spawn_id = Column(String(255), unique=True, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(Integer, nullable=True)
    
    # Spawned Pokémon
    species = Column(String(255), nullable=False)
    species_id = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    is_shiny = Column(Boolean, default=False, nullable=False)
    rarity = Column(SQLEnum(PokemonRarity), default=PokemonRarity.COMMON, nullable=False)
    
    # Spawn state
    is_caught = Column(Boolean, default=False, nullable=False, index=True)
    caught_by = Column(BigInteger, nullable=True)
    caught_at = Column(DateTime, nullable=True)
    
    # Timestamps
    spawned_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)


class Battle(Base):
    """Battle table."""
    __tablename__ = "battles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    battle_id = Column(String(255), unique=True, nullable=False, index=True)
    challenger_id = Column(BigInteger, nullable=False, index=True)
    defender_id = Column(BigInteger, nullable=True, index=True)
    
    # Battle configuration
    battle_type = Column(String(50), default="pve", nullable=False)
    status = Column(SQLEnum(BattleStatus), default=BattleStatus.PENDING, nullable=False, index=True)
    
    # Teams (stored as JSON arrays)
    challenger_team = Column(JSON, default=list)
    defender_team = Column(JSON, default=list)
    
    # Battle state
    current_turn = Column(Integer, default=0, nullable=False)
    challenger_current_pokemon = Column(Integer, nullable=True)
    defender_current_pokemon = Column(Integer, nullable=True)
    
    # Results (stored as JSON)
    winner_id = Column(BigInteger, nullable=True)
    experience_gained = Column(JSON, default=dict)
    rewards = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)


class Trade(Base):
    """Trade table."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(255), unique=True, nullable=False, index=True)
    initiator_id = Column(BigInteger, nullable=False, index=True)
    target_id = Column(BigInteger, nullable=False, index=True)
    
    # Trade items (stored as JSON)
    initiator_pokemon = Column(JSON, default=list)
    initiator_items = Column(JSON, default=dict)
    initiator_coins = Column(BigInteger, default=0)
    
    target_pokemon = Column(JSON, default=list)
    target_items = Column(JSON, default=dict)
    target_coins = Column(BigInteger, default=0)
    
    # Trade state
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.PENDING, nullable=False, index=True)
    initiator_confirmed = Column(Boolean, default=False, nullable=False)
    target_confirmed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)


class Quest(Base):
    """Quest/Mission table."""
    __tablename__ = "quests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quest_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # Quest details
    quest_type = Column(String(50), nullable=False)  # "daily", "weekly", "monthly", "special"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Requirements
    target_type = Column(String(50), nullable=False)  # "catch", "battle", "evolve", etc.
    target_count = Column(Integer, nullable=False)
    current_count = Column(Integer, default=0, nullable=False)
    
    # Rewards (stored as JSON)
    reward_coins = Column(Integer, default=0, nullable=False)
    reward_items = Column(JSON, default=dict)
    reward_exp = Column(Integer, default=0, nullable=False)
    
    # Status
    is_completed = Column(Boolean, default=False, nullable=False)
    is_claimed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class SpawnCooldown(Base):
    """Spawn cooldown table (replaces Redis)."""
    __tablename__ = "spawn_cooldowns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, unique=True, index=True)
    last_spawn = Column(DateTime, nullable=False)
    cooldown_until = Column(DateTime, nullable=False, index=True)
