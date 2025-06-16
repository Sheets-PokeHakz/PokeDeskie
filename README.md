# PokeDex Discord Bot

A comprehensive Discord bot for Pokemon enthusiasts with gambling features, Pokemon information lookup, and trade tracking.

## Features

### 🎮 Pokemon Features

- **Pokemon Search**: Look up Pokemon by name or Pokedex number
- **Random Pokemon Roll**: Roll random Pokemon with detailed stats
- **Auto-Dex Integration**: Automatically responds to other Pokemon bots with enhanced information

### 🎲 Gambling System

- **User Registration**: Register to participate in gambling features
- **Profile System**: Track your gambling statistics and earnings
- **Leaderboards**: Compete with other users on earnings and activity
- **Trade Tracking**: Automatically track and log Pokemon trades

### 🛠️ Admin Features

- **User Management**: Add/remove coins from user accounts
- **Profile Viewing**: View any user's profile
- **Database Management**: Automatic daily backups

## Project Structure

``` bash
PokeDeskie/
├── bot.py              # Main bot entry point
├── config.py           # Configuration management
├── database.py         # Database operations
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── cogs/               # Command modules
│   ├── admin.py        # Admin commands
│   ├── events.py       # Event handlers
│   ├── gambling.py     # Gambling commands
│   ├── help.py         # Help command
│   └── pokemon.py      # Pokemon commands
├── Config.json         # Bot configuration
├── PokeDex.json        # Pokemon data
├── Profile.db          # User database
└── Trades.json         # Trade logs
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord bot token
- Discord server with appropriate permissions

### 2. Installation

1. **Clone/Download the project**

   ```bash
   cd PokeDeskie
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   export BOT_TOKEN="your_discord_bot_token_here"
   ```

   Or create a `.env` file:

   ```bash
   BOT_TOKEN=your_discord_bot_token_here
   ```

4. **Configure the bot**
   Edit `Config.json` to set up your channels:

   ```json
   {
       "trade_log": 123456789,
       "rand_channels": [123456789, 987654321],
       "trade_channels": [123456789],
       "WEBHOOK_URL": "your_webhook_url_for_backups"
   }
   ```

5. **Run the bot**

   ```bash
   python bot.py
   ```

## Commands

### User Commands

- `+register` - Register in the gambling system
- `+profile` / `+p` [user] - View gambling profile
- `+leaderboard` / `+lb` - View earnings leaderboard
- `+leaderboardgambles` / `+lbg` - View activity leaderboard
- `+ping` - Check bot status and uptime
- `+roll` / `+r` - Roll a random Pokemon
- `+search` / `+poke` <name/number> - Search for Pokemon
- `+help` - Show help information

### Admin Commands

- `+adminprofile` / `+ap` <user> - View any user's profile
- `+addnet` / `+anet` <user> <amount> - Add coins to user
- `+removenet` / `+rnet` <user> <amount> - Remove coins from user

## Configuration

### Channel Types

- **Random Channels**: Channels where Pokemon information is automatically displayed
- **Trade Channels**: Channels where trade activities are monitored
- **Trade Log**: Channel where trade logs are posted

### Bot Integration

The bot integrates with several Pokemon bots:

- **Carl Bot** (ID: 235148962103951360)
- **PK2 Assistant** (ID: 854233015475109888)
- **YAMPB** (ID: 204255221017214977)
- **Poketwo** (ID: 716390085896962058)

## Database Schema

The bot uses SQLite with the following user table structure:

```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    net_total INTEGER DEFAULT 0,
    max_gambled INTEGER DEFAULT 0,
    gamble_wins INTEGER DEFAULT 0,
    gamble_losses INTEGER DEFAULT 0,
    gamble_wins_streak INTEGER DEFAULT 0,
    gamble_losses_streak INTEGER DEFAULT 0
);
```

## File Descriptions

### Core Files

- **`bot.py`**: Main entry point, handles bot initialization and cog loading
- **`config.py`**: Configuration management with environment variable support
- **`database.py`**: Database operations with connection pooling and error handling
- **`utils.py`**: Utility functions for Pokemon data, embeds, and formatting

### Cogs (Command Modules)

- **`admin.py`**: Administrator commands for user management
- **`events.py`**: Event handlers for messages, trades, and bot integration
- **`gambling.py`**: User registration, profiles, and leaderboards
- **`help.py`**: Help command with dynamic admin command display
- **`pokemon.py`**: Pokemon search and random roll functionality

## Development Notes

### Key Improvements Made

1. **Modular Structure**: Separated code into logical modules and cogs
2. **Error Handling**: Comprehensive error handling throughout
3. **Database Safety**: Context managers for database connections
4. **Configuration Management**: Centralized config with environment variable support
5. **Code Documentation**: Extensive docstrings and comments
6. **Type Hints**: Added where appropriate for better code maintainability

### Best Practices Implemented

- **Single Responsibility**: Each module has a clear, focused purpose
- **DRY Principle**: Eliminated code duplication
- **Error Recovery**: Graceful handling of missing data and failed operations
- **Security**: No hardcoded tokens, proper permission checks
- **Maintainability**: Clear structure and documentation

## Troubleshooting

### Common Issues

1. **Bot won't start**: Check if BOT_TOKEN is set correctly
2. **Commands not working**: Verify bot has necessary permissions
3. **Database errors**: Ensure write permissions in bot directory
4. **Pokemon data missing**: Check if PokeDex.json exists and is valid

### Logging

The bot provides console output for:

- Successful cog loading
- Database operations
- Error conditions
- Trade processing

## Contributing

When contributing to this project:

1. Follow the existing code structure
2. Add appropriate error handling
3. Include docstrings for new functions
4. Test thoroughly before submitting
5. Update documentation as needed

## License

This project is provided as-is for educational and personal use.
