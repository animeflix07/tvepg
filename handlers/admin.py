import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import OWNER_ID
from database.db import Database
from utils.notification import notify_user

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("addpremium"))
async def add_premium_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can execute this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /addpremium <user_id> <days> (0 for permanent)")
        return

    try:
        user_id = int(args[1])
        days = int(args[2])

        user = await Database.get_user(user_id)
        if not user:
            await Database.create_user(user_id)

        await Database.add_premium(user_id, days, message.from_user.id)

        if days == 0:
            msg = "🎉 Premium Access Granted! (Permanent)"
        else:
            msg = f"🎉 Premium Access Granted! ({days} days)"

        await notify_user(user_id, msg)
        await message.answer(f"✅ Premium added for user {user_id}")

    except ValueError:
        await message.answer("❌ Invalid arguments. Use: /addpremium <user_id> <days>")
    except Exception as e:
        logger.error(f"Add premium error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("removepremium"))
async def remove_premium_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can execute this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /removepremium <user_id>")
        return

    try:
        user_id = int(args[1])
        await Database.remove_premium(user_id)
        await notify_user(user_id, "⚠️ Premium Access Removed")
        await message.answer(f"✅ Premium removed for user {user_id}")
    except ValueError:
        await message.answer("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Remove premium error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("ban"))
async def ban_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can execute this command.")
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("Usage: /ban <user_id> [reason]")
        return

    try:
        user_id = int(args[1])
        reason = args[2] if len(args) > 2 else None

        await Database.ban_user(user_id, message.from_user.id, reason)
        await notify_user(user_id, "🚫 You have been banned.")
        await message.answer(f"✅ User {user_id} banned")
    except ValueError:
        await message.answer("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Ban error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("unban"))
async def unban_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can execute this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /unban <user_id>")
        return

    try:
        user_id = int(args[1])
        await Database.unban_user(user_id)
        await notify_user(user_id, "✅ You have been unbanned.")
        await message.answer(f"✅ User {user_id} unbanned")
    except ValueError:
        await message.answer("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Unban error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("maintenance"))
async def maintenance_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can execute this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /maintenance <on|off>")
        return

    mode = args[1].lower()
    if mode not in ["on", "off"]:
        await message.answer("Usage: /maintenance <on|off>")
        return

    try:
        await Database.set_config("maintenance_mode", mode)
        await message.answer(f"✅ Maintenance mode turned {mode}")
    except Exception as e:
        logger.error(f"Maintenance error: {e}")
        await message.answer(f"❌ Error: {str(e)}")
