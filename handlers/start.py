import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import OWNER_ID
from database.db import Database

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user = await Database.get_user(user_id)

    if not user:
        await Database.create_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )

    if user_id == OWNER_ID:
        welcome_text = """
🎬 Welcome to JioTV Telegram Bot - Owner Dashboard

You are the owner of this bot. Use /help to see all available commands.

Available commands:
• /login - Login with Jio credentials
• /categories - Browse all channels
• /search - Search for channels
• /epg - Get channel EPG
• /record - Record live stream
• /catchup - Watch catch-up content
• /addpremium - Add premium user
• /removepremium - Remove premium user
• /ban - Ban user
• /unban - Unban user
• /maintenance - Toggle maintenance mode
"""
    else:
        user_status = ""
        if user and user.get("is_premium"):
            user_status = "✅ Premium Member"
        else:
            welcome_text = """
🔒 Access Restricted

❌ You are not authorized to use this bot.

This is a premium bot. Contact @II_Madara_II to get access.
"""
            await message.answer(welcome_text)
            return

        welcome_text = f"""
🎬 Welcome to JioTV Telegram Bot

Status: {user_status}

Available commands:
• /categories - Browse all channels
• /search - Search for channels
• /epg - Get channel EPG
• /record - Record live stream
• /catchup - Watch catch-up content
"""

    await message.answer(welcome_text)
