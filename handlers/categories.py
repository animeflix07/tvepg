import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.jiotv_wrapper import JioTVWrapper

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("categories"))
async def categories_command(message: types.Message):
    try:
        jio = JioTVWrapper()
        categories = await jio.get_categories()

        if not categories:
            await message.answer("❌ No categories available.")
            return

        keyboard = []
        for cat in categories:
            keyboard.append([
                InlineKeyboardButton(
                    text=cat.get("name", "Unknown"),
                    callback_data=f"cat_{cat.get('id')}"
                )
            ])

        await message.answer(
            "📺 Select a category:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    except Exception as e:
        logger.error(f"Categories error: {e}")
        await message.answer(f"❌ Error loading categories: {str(e)}")

@router.callback_query(F.data.startswith("cat_"))
async def category_selected(callback: types.CallbackQuery):
    category_id = callback.data.replace("cat_", "")

    try:
        jio = JioTVWrapper()
        channels = await jio.get_channels_by_category(category_id)

        if not channels:
            await callback.answer("No channels found.", show_alert=True)
            return

        channel_text = "📺 Channels in this category:\n\n"
        for ch in channels:
            channel_text += f"• {ch.get('name')} (ID: {ch.get('channel_id')})\n"
            channel_text += f"  Languages: {', '.join(ch.get('languages', []))}\n\n"

        await callback.message.edit_text(channel_text)
        await callback.answer()
    except Exception as e:
        logger.error(f"Channel listing error: {e}")
        await callback.answer(f"Error: {str(e)}", show_alert=True)
