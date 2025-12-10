# JioTV Telegram Bot

A feature-rich Telegram bot that integrates with JioTV for live streaming, recording, and catch-up content management.

## Features

- **User Management**
  - Owner-only login with auto token refresh
  - Premium user system with expiry tracking
  - User ban/unban functionality
  - Maintenance mode

- **Channel Features**
  - Browse categories and channels
  - Search channels
  - View EPG information
  - Access catch-up content

- **Recording & Download**
  - Record live streams with automatic FFmpeg encoding
  - Download catch-up content
  - MKV format with full metadata injection
  - Automatic filename formatting

- **Quality Features**
  - Multi-language audio track detection
  - Automatic codec detection
  - Resolution tracking
  - Metadata embedding

## Installation

### Requirements
- Python 3.11+
- MongoDB
- FFmpeg
- MKVToolNix

### Setup

1. Clone the repository
\`\`\`bash
git clone <repo-url>
cd jiotv_telegram_bot
\`\`\`

2. Create .env file
\`\`\`bash
cp .env.example .env
# Edit .env with your credentials
\`\`\`

3. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Run with Docker Compose
\`\`\`bash
docker-compose up -d
\`\`\`

Or run directly:
\`\`\`bash
python app.py
\`\`\`

## Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/categories` - Browse TV categories
- `/search <query>` - Search channels
- `/epg <channel>` - Get channel EPG
- `/premium` - Check premium status

### Recording Commands
- `/record <channel> <HH:MM:SS>` - Record live stream
- `/catchup <channel>` - Get catch-up content
- `/dl -c <channel> -d <DD-MM-YYYY> -t <start> - <end>` - Download episode

### Admin Commands (Owner only)
- `/login` - Login with JioTV credentials
- `/addpremium <user_id> <days>` - Add premium (0=permanent)
- `/removepremium <user_id>` - Remove premium
- `/ban <user_id>` - Ban user
- `/unban <user_id>` - Unban user
- `/maintenance <on|off>` - Toggle maintenance mode

## Configuration

Edit `.env` file to configure:
- `BOT_TOKEN` - Your Telegram Bot Token
- `OWNER_ID` - Your Telegram User ID
- `MONGODB_URI` - MongoDB connection string
- `JIOTV_API_URL` - JioTV API endpoint

## Database

MongoDB collections:
- `users` - User profiles and credentials
- `premium` - Premium membership records
- `banned` - Banned users list
- `config` - Bot configuration
- `recordings` - Recording history

## File Structure

\`\`\`
jiotv_telegram_bot/
├── handlers/          # Command handlers
├── database/          # Database models and operations
├── middlewares/       # Access control middleware
├── utils/             # Utility functions
├── config.py          # Configuration
├── app.py             # Main bot entry point
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker compose
\`\`\`

## Deployment

### Using Docker
\`\`\`bash
docker-compose up -d
\`\`\`

### Using bot-hosting.net
1. Download the repository as ZIP
2. Upload to bot-hosting.net
3. Set environment variables
4. Deploy

## Security

- JioTV credentials stored securely in MongoDB
- Row-level access control via middleware
- Ban system for malicious users
- Maintenance mode for updates

## License

MIT License

## Support

For issues and support, contact @II_Madara_II
