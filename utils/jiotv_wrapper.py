import logging
import aiohttp
from config import JIOTV_API_URL

logger = logging.getLogger(__name__)

class JioTVWrapper:
    def __init__(self):
        self.base_url = JIOTV_API_URL

    async def request_otp(self, phone: str):
        """Request OTP for login"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/login/request_otp"
                async with session.post(url, json={"phone": phone}) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"OTP request error: {e}")
            return {"status": "error", "message": str(e)}

    async def verify_otp(self, phone: str, otp: str):
        """Verify OTP and get token"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/login/verify_otp"
                async with session.post(url, json={"phone": phone, "otp": otp}) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return {"status": "error", "message": str(e)}

    async def get_categories(self):
        """Get all TV categories"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/categories"
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data.get("categories", [])
        except Exception as e:
            logger.error(f"Categories error: {e}")
            return []

    async def get_channels_by_category(self, category_id: str):
        """Get channels for a category"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/channels?category_id={category_id}"
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data.get("channels", [])
        except Exception as e:
            logger.error(f"Channel listing error: {e}")
            return []

    async def search_channels(self, query: str):
        """Search for channels"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/search?q={query}"
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def get_epg(self, channel: str):
        """Get EPG for a channel"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/epg?channel={channel}"
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data.get("epg", [])
        except Exception as e:
            logger.error(f"EPG error: {e}")
            return []

    async def get_stream_url(self, channel: str):
        """Get live stream URL"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/stream?channel={channel}"
                async with session.get(url) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Stream URL error: {e}")
            return None

    async def get_catchup(self, channel: str):
        """Get catch-up content"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/catchup?channel={channel}"
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data.get("catchup", [])
        except Exception as e:
            logger.error(f"Catch-up error: {e}")
            return []

    async def get_catchup_url(self, channel: str, date: str, start_time: str, end_time: str):
        """Get catch-up stream URL"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/catchup/stream"
                params = {
                    "channel": channel,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time
                }
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    return data.get("url")
        except Exception as e:
            logger.error(f"Catch-up URL error: {e}")
            return None
