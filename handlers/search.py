import logging
from aiogram import Router, types
from aiogram.filters import Command
from utils.jiotv_wrapper import JioTVWrapper

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("search"))
async def search_command(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Usage: /search <channel_name>")
        return

    query = args[1]

    try:
        jio = JioTVWrapper()
        results = await jio.search_channels(query)

        if not results:
            await message.answer(f"❌ No channels found for '{query}'")
            return

        response = f"🔍 Search results for '{query}':\n\n"
        for ch in results:
            response += f"📺 {ch.get('name')} (ID: {ch.get('channel_id')})\n"
            response += f"   Languages: {', '.join(ch.get('languages', []))}\n\n"

        await message.answer(response)
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer(f"❌ Error: {str(e)}")
