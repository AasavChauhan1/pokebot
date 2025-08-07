# Pokémon Telegram Bot

A feature-rich Pokémon-themed Telegram bot with spawning, battles, trading, inventory, and economy systems.

## Features

### 🟢 Core Features
- **Pokémon Spawning & Claiming**: Random spawns with rarity-based system
- **Battle System**: PvP and AI battles with turn-based combat
- **Inventory & Items**: Poké Balls, potions, berries, evolution stones
- **Trading System**: Safe trading between users
- **Leveling & Evolution**: EXP system with auto-evolution
- **Daily Streaks & Quests**: Daily rewards and missions
- **Trainer Profile**: Comprehensive user statistics
- **Leaderboards**: Global and group rankings
- **Market & Store**: In-game economy with items and gacha

### ✨ Additional Features
- Mini-games (coin flip, slots, quiz)
- Guilds/Clans system
- Badge achievements
- Multilingual support
- Admin panel

## Tech Stack

- **Backend**: Python with python-telegram-bot
- **Database**: MongoDB for data persistence
- **Cache**: Redis for sessions and cooldowns
- **External API**: PokeAPI for Pokémon data
- **Image Processing**: Pillow for image manipulation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Run the bot:
```bash
python main.py
```

## Project Structure

```
pokebot/
├── bot/                    # Main bot module
│   ├── handlers/          # Command and callback handlers
│   ├── models/            # Database models
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   └── __init__.py
├── config/                # Configuration files
├── data/                  # Static data and assets
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── main.py               # Entry point
└── README.md             # This file
```

## Environment Variables

- `BOT_TOKEN`: Your Telegram bot token
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string
- `ADMIN_IDS`: Comma-separated admin user IDs
- `DEBUG`: Enable debug mode (True/False)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
