import logging
from aiogram import Router, types
from aiogram.filters import Command
from utils.jiotv_wrapper import JioTVWrapper

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("epg"))
async def epg_command(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Usage: /epg <channel_name_or_id>")
        return

    channel = args[1]

    try:
        jio = JioTVWrapper()
        epg_data = await jio.get_epg(channel)

        if not epg_data:
            await message.answer(f"❌ No EPG data found for '{channel}'")
            return

        response = f"📅 EPG for {channel}:\n\n"
        for program in epg_data:
            response += f"⏰ {program.get('start_time')} - {program.get('end_time')}\n"
            response += f"📺 {program.get('title')}\n"
            if program.get('description'):
                response += f"📝 {program.get('description')}\n"
            response += "\n"

        await message.answer(response)
    except Exception as e:
        logger.error(f"EPG error: {e}")
        await message.answer(f"❌ Error: {str(e)}")
