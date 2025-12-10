import logging
from aiogram import Bot
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

async def notify_user(user_id: int, message: str):
    """Send notification to user"""
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(user_id, message)
    except Exception as e:
        logger.error(f"Notification error: {e}")
