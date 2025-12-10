import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

try:
    from config import BOT_TOKEN, MONGODB_URI
except ImportError as e:
    logging.error(f"Failed to import config: {e}")
    raise

try:
    from database.db import init_db
except ImportError as e:
    logging.error(f"Failed to import database: {e}")
    raise

try:
    from middlewares.access_control import AccessControlMiddleware
except ImportError as e:
    logging.error(f"Failed to import middlewares: {e}")
    raise

try:
    from handlers import start, auth, categories, search, epg, record, catchup, download, admin
    from handlers import help as help_handler
except ImportError as e:
    logging.error(f"Failed to import handlers: {e}")
    raise

# Setup logging with better configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot startup function"""
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")

        # Validate bot token
        if not BOT_TOKEN or BOT_TOKEN == "":
            raise ValueError("BOT_TOKEN is not set in environment variables")

        logger.info("Creating bot instance...")
        bot = Bot(token=BOT_TOKEN)

        # Test bot connection
        try:
            bot_info = await bot.get_me()
            logger.info(f"Bot connected successfully: @{bot_info.username}")
        except Exception as e:
            logger.error(f"Failed to connect to bot: {e}")
            raise

        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        logger.info("Registering middlewares...")
        dp.message.middleware(AccessControlMiddleware())
        dp.callback_query.middleware(AccessControlMiddleware())

        logger.info("Registering routers...")
        dp.include_router(start.router)
        dp.include_router(auth.router)
        dp.include_router(categories.router)
        dp.include_router(search.router)
        dp.include_router(epg.router)
        dp.include_router(record.router)
        dp.include_router(catchup.router)
        dp.include_router(download.router)
        dp.include_router(admin.router)
        dp.include_router(help_handler.router)

        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        try:
            await bot.session.close()
            logger.info("Bot session closed")
        except Exception as e:
            logger.error(f"Error closing bot session: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        exit(1)
