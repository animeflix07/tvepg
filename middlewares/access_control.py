import logging
from datetime import datetime
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from database.db import Database

logger = logging.getLogger(__name__)

class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any], Awaitable[Any]],
        event: Any,
        data: dict[str, Any]
    ) -> Any:
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id
            # Update last active
            await Database.update_user(user_id, {"last_active": datetime.utcnow()})
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            # Check if user is banned
            if await Database.is_banned(user_id):
                if isinstance(event, Message):
                    await event.answer("🚫 You have been banned.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 You have been banned.", show_alert=True)
                return

            # Check maintenance mode
            if user_id != OWNER_ID:
                maintenance = await Database.get_config("maintenance_mode")
                if maintenance == "on":
                    if isinstance(event, Message):
                        await event.answer("🚧 Maintenance Mode Enabled")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("🚧 Maintenance Mode Enabled", show_alert=True)
                    return

            # Check premium expiry
            if await Database.check_premium_expired(user_id):
                if isinstance(event, Message):
                    await event.answer("⚠️ Premium Access Expired")

        return await handler(event, data)
