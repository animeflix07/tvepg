import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DB_NAME
from database.models import User, PremiumRecord, BannedUser, Config
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

    @staticmethod
    async def init_db():
        try:
            Database.client = AsyncIOMotorClient(MONGODB_URI)
            Database.db = Database.client[DB_NAME]

            # Test connection
            await Database.client.admin.command('ping')
            logger.info("Database connected successfully")

            # Create collections
            collections = ['users', 'premium', 'banned', 'config', 'recordings']
            existing_collections = await Database.db.list_collection_names()

            for collection in collections:
                if collection not in existing_collections:
                    await Database.db.create_collection(collection)
                    logger.info(f"Created collection: {collection}")

            # Create indexes
            pipeline = [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            duplicates = await Database.db.users.aggregate(pipeline).to_list(None)
            for dup in duplicates:
                docs_to_delete = dup['docs'][1:]
                await Database.db.users.delete_many({"_id": {"$in": docs_to_delete}})

            try:
                await Database.db.users.drop_index("user_id_1")
            except Exception:
                pass
            await Database.db.users.create_index("user_id", unique=True)
            await Database.db.premium.create_index("user_id")
            await Database.db.banned.create_index("user_id", unique=True)

            pipeline = [
                {"$group": {"_id": "$recording_id", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            duplicates = await Database.db.recordings.aggregate(pipeline).to_list(None)
            for dup in duplicates:
                docs_to_delete = dup['docs'][1:]
                await Database.db.recordings.delete_many({"_id": {"$in": docs_to_delete}})
            await Database.db.recordings.create_index("recording_id", unique=True)

            logger.info("Database initialized successfully with all indexes")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @staticmethod
    async def close_db():
        try:
            if Database.client:
                Database.client.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

    # User operations
    @staticmethod
    async def get_user(user_id: int):
        return await Database.db.users.find_one({"user_id": user_id})

    @staticmethod
    async def create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "is_premium": False,
            "is_banned": False,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        try:
            result = await Database.db.users.insert_one(user_data)
            logger.info(f"Created user: {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            raise

    @staticmethod
    async def update_user(user_id: int, update_data: dict):
        try:
            return await Database.db.users.update_one(
                {"user_id": user_id},
                {"$set": {**update_data, "last_active": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    # Premium operations
    @staticmethod
    async def add_premium(user_id: int, days: int, granted_by: int):
        try:
            expiry = None if days == 0 else datetime.utcnow() + timedelta(days=days)
            premium_data = {
                "user_id": user_id,
                "granted_by": granted_by,
                "granted_at": datetime.utcnow(),
                "expiry_date": expiry,
                "is_permanent": days == 0,
                "duration_days": days if days > 0 else None
            }
            await Database.db.premium.insert_one(premium_data)
            await Database.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_premium": True, "premium_expiry": expiry}}
            )
            logger.info(f"Added premium to user {user_id}")
        except Exception as e:
            logger.error(f"Error adding premium to user {user_id}: {e}")
            raise

    @staticmethod
    async def remove_premium(user_id: int):
        try:
            await Database.db.premium.delete_one({"user_id": user_id})
            await Database.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )
            logger.info(f"Removed premium from user {user_id}")
        except Exception as e:
            logger.error(f"Error removing premium from user {user_id}: {e}")
            raise

    @staticmethod
    async def check_premium_expired(user_id: int):
        try:
            user = await Database.get_user(user_id)
            if user and user.get("premium_expiry"):
                if user["premium_expiry"] < datetime.utcnow():
                    await Database.remove_premium(user_id)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking premium expiry for user {user_id}: {e}")
            return False

    # Ban operations
    @staticmethod
    async def ban_user(user_id: int, banned_by: int, reason: str = None):
        try:
            ban_data = {
                "user_id": user_id,
                "banned_by": banned_by,
                "reason": reason,
                "banned_at": datetime.utcnow()
            }
            await Database.db.banned.insert_one(ban_data)
            await Database.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": True}}
            )
            logger.info(f"Banned user {user_id}")
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            raise

    @staticmethod
    async def unban_user(user_id: int):
        try:
            await Database.db.banned.delete_one({"user_id": user_id})
            await Database.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": False}}
            )
            logger.info(f"Unbanned user {user_id}")
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            raise

    @staticmethod
    async def is_banned(user_id: int):
        try:
            return await Database.db.banned.find_one({"user_id": user_id}) is not None
        except Exception as e:
            logger.error(f"Error checking ban status for user {user_id}: {e}")
            return False

    # Config operations
    @staticmethod
    async def get_config(key: str):
        try:
            result = await Database.db.config.find_one({"key": key})
            return result.get("value") if result else None
        except Exception as e:
            logger.error(f"Error getting config {key}: {e}")
            return None

    @staticmethod
    async def set_config(key: str, value: str):
        try:
            await Database.db.config.update_one(
                {"key": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            logger.info(f"Set config {key}")
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            raise

    # Recording operations
    @staticmethod
    async def create_recording(recording_id: str, user_id: int, channel_id: str,
                              channel_name: str, start_time, end_time):
        try:
            recording_data = {
                "recording_id": recording_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "start_time": start_time,
                "end_time": end_time,
                "status": "recording",
                "created_at": datetime.utcnow()
            }
            await Database.db.recordings.insert_one(recording_data)
            logger.info(f"Created recording: {recording_id}")
        except Exception as e:
            logger.error(f"Error creating recording {recording_id}: {e}")
            raise

    @staticmethod
    async def update_recording(recording_id: str, update_data: dict):
        try:
            return await Database.db.recordings.update_one(
                {"recording_id": recording_id},
                {"$set": update_data}
            )
        except Exception as e:
            logger.error(f"Error updating recording {recording_id}: {e}")
            raise

    @staticmethod
    async def get_recording(recording_id: str):
        try:
            return await Database.db.recordings.find_one({"recording_id": recording_id})
        except Exception as e:
            logger.error(f"Error getting recording {recording_id}: {e}")
            return None

async def init_db():
    await Database.init_db()
