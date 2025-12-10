import asyncio
from database.db import Database

async def init():
    await Database.init_db()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init())
