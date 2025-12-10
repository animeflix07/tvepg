import logging
from aiogram import Router, types
from aiogram.filters import Command
from utils.jiotv_wrapper import JioTVWrapper

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("catchup"))
async def catchup_command(message: types.Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Usage: /catchup <channel_name>")
        return

    channel_name = args[1]

    try:
        jio = JioTVWrapper()
        catchup_data = await jio.get_catchup(channel_name)

        if not catchup_data:
            await message.answer(f"❌ No catch-up data for {channel_name}")
            return

        response = f"📺 Catch-up for {channel_name}:\n\n"
        for item in catchup_data:
            response += f"📅 {item.get('date')}\n"
            response += f"⏰ {item.get('start_time')} - {item.get('end_time')}\n"
            response += f"📝 {item.get('title')}\n\n"

        await message.answer(response)
    except Exception as e:
        logger.error(f"Catch-up error: {e}")
        await message.answer(f"❌ Error: {str(e)}")
