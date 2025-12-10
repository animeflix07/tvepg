import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import OWNER_ID

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("help"))
async def help_command(message: types.Message):
    user_id = message.from_user.id

    if user_id == OWNER_ID:
        help_text = """
🤖 JioTV Telegram Bot - Command Help

🎬 USER COMMANDS:
/start - Start the bot
/help - Show this message
/categories - Browse all TV categories
/search <query> - Search for channels
/epg <channel> - Get channel EPG
/premium - Check premium status

🎥 RECORDING COMMANDS:
/record <channel> <HH:MM:SS> - Record live stream
/catchup <channel> - Get catch-up content
/dl -c <channel> -d <DD-MM-YYYY> -t <start_time> - <end_time> - Download catch-up

👨‍💼 ADMIN COMMANDS:
/addpremium <user_id> <days> - Add premium (0=permanent)
/removepremium <user_id> - Remove premium
/ban <user_id> [reason] - Ban user
/unban <user_id> - Unban user
/maintenance <on|off> - Toggle maintenance mode
/login - Login with Jio credentials

📝 EXAMPLES:
/search sony - Search for Sony channels
/epg sony_sab - Get Sony SAB EPG
/record sony_sab 01:30:00 - Record for 1.5 hours
/dl -c sony_sab -d 10-12-2024 -t 20:00 - 22:00 - Download episode
/addpremium 123456789 30 - Add 30-day premium
/ban 123456789 Spamming - Ban user for spamming
"""
    else:
        help_text = """
🤖 JioTV Telegram Bot - Command Help

🎬 AVAILABLE COMMANDS:
/start - Start the bot
/help - Show this message
/categories - Browse all TV categories
/search <query> - Search for channels
/epg <channel> - Get channel EPG
/premium - Check premium status

📝 EXAMPLES:
/search sony - Search for Sony channels
/epg sony_sab - Get Sony SAB EPG

🔒 For access, contact @II_Madara_II
"""

    await message.answer(help_text)
