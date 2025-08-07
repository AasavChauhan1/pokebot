# 🔥 PokéBot Development Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- Redis
- Telegram Bot Token

### Installation

1. **Clone and setup:**
```bash
cd pokebot
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your values
```

3. **Setup database:**
```bash
python setup.py
```

4. **Run the bot:**
```bash
python main.py
```

## 🛠️ Development

### Project Structure
```
pokebot/
├── bot/                    # Main bot logic
│   ├── handlers/          # Command handlers
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── config/                # Configuration
├── data/                  # Static data
├── tests/                 # Unit tests
└── main.py               # Entry point
```

### Key Services

#### UserService
Manages trainer/user data:
- User creation and retrieval
- Experience and leveling
- Coin management
- Daily rewards
- Battle statistics

#### PokemonService
Manages Pokémon data:
- Pokémon creation and stats
- Team management
- Experience and leveling
- Evolution handling

#### SpawnService
Manages Pokémon spawning:
- Random spawning with cooldowns
- Rarity-based generation
- Catch mechanics
- Auto-spawn in groups

#### BattleService
Manages battles:
- PvP and PvE battles
- Turn-based combat
- Experience rewards
- AI opponents

### Development Commands

```bash
# Create test data
python dev.py create-test-data

# View statistics
python dev.py stats

# Run tests
python dev.py test

# Clean up test data
python dev.py cleanup-test-data

# Reset database (DANGEROUS!)
python dev.py reset-database
```

## 🎮 Bot Commands

### Basic Commands
- `/start` - Begin your journey
- `/help` - Command list
- `/profile` - View profile

### Pokémon Management
- `/pokemon` or `/p` - View collection
- `/team` - Manage battle team
- `/catch` or `/c` - Catch spawned Pokémon
- `/spawn` - Manual spawn (limited)

### Battles (Planned)
- `/battle @user` - Challenge trainer
- `/battle wild` - Fight wild Pokémon

### Economy (Planned)
- `/shop` - Browse items
- `/daily` - Daily rewards
- `/trade @user` - Trade with others

### Admin Commands
- `/admin stats` - Bot statistics
- `/admin user <id>` - User info
- `/admin give <user> <pokemon>` - Give Pokémon

## 🏗️ Architecture

### Database Schema

#### Users Collection
```javascript
{
  user_id: Number,
  username: String,
  trainer_level: Number,
  experience: Number,
  coins: Number,
  daily_streak: Number,
  battles_won: Number,
  // ... more fields
}
```

#### Pokemon Collection
```javascript
{
  pokemon_id: String,
  owner_id: Number,
  species: String,
  level: Number,
  hp: Number, attack: Number, // stats
  nature: String,
  is_shiny: Boolean,
  in_team: Boolean,
  // ... more fields
}
```

#### Spawns Collection
```javascript
{
  spawn_id: String,
  chat_id: Number,
  species: String,
  level: Number,
  is_caught: Boolean,
  spawned_at: Date,
  expires_at: Date
}
```

### Redis Usage
- Spawn cooldowns: `last_spawn:{chat_id}`
- User cooldowns: `user_spawn_cooldown:{user_id}`
- Session data and caching

## 🎯 Features Implementation Status

### ✅ Implemented
- [x] User registration and profiles
- [x] Pokémon spawning system
- [x] Catching mechanics
- [x] Collection management
- [x] Team management
- [x] Basic battle system
- [x] Admin commands
- [x] PokeAPI integration
- [x] Rarity system
- [x] Shiny Pokémon
- [x] Daily rewards
- [x] Experience and leveling

### 🚧 In Progress
- [ ] Trading system
- [ ] Quest system
- [ ] Advanced battles
- [ ] Item system
- [ ] Evolution system

### 📋 Planned
- [ ] Mini-games
- [ ] Guilds/Clans
- [ ] Marketplace
- [ ] Leaderboards
- [ ] Achievement system
- [ ] Multilingual support

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/ -v
```

Test coverage includes:
- Utility functions
- Data models
- Core game mechanics
- Database operations (with mocks)

## 🐛 Debugging

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **Database Connection**
   - Verify MongoDB and Redis are running
   - Check connection strings in .env

3. **API Limits**
   - PokeAPI has rate limits
   - Implement caching for production

### Logging
Logs are written to:
- Console (stdout)
- `pokebot.log` file

Log levels can be configured via `LOG_LEVEL` environment variable.

## 🚀 Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up monitoring
- [ ] Enable HTTPS for webhooks
- [ ] Set up backup strategy
- [ ] Configure error reporting

### Docker Deployment
```bash
# Build image
docker build -t pokebot .

# Run with docker-compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

## 📚 Resources

- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)

## 📄 License

MIT License - see LICENSE file for details.
