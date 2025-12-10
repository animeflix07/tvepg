import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Database
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "Cluster0")

MONGODB_URI = DB_URL

# JioTV
JIOTV_API_URL = os.getenv("JIOTV_API_URL", "http://localhost:5001")
JIOTV_TIMEOUT = int(os.getenv("JIOTV_TIMEOUT", "10"))
JIOTV_RETRY_ATTEMPTS = int(os.getenv("JIOTV_RETRY_ATTEMPTS", "3"))

# FFmpeg
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")
MKVMERGE_PATH = os.getenv("MKVMERGE_PATH", "/usr/bin/mkvmerge")

# Storage - Use /tmp and /home directories instead of read-only /data
TEMP_DIR = os.getenv("TEMP_DIR", "./temp/jiotv_bot")
RECORDINGS_DIR = os.getenv("RECORDINGS_DIR", "./temp/recordings")
DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", "./temp/downloads")

# Bot Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))
MAX_CONCURRENT_RECORDINGS = int(os.getenv("MAX_CONCURRENT_RECORDINGS", "2"))

# Notification Settings
SEND_NOTIFICATIONS = os.getenv("SEND_NOTIFICATIONS", "true").lower() == "true"
NOTIFICATION_DELAY = int(os.getenv("NOTIFICATION_DELAY", "5"))

# Telegram media limits
MAX_VIDEO_SIZE = 2000 * 1024 * 1024  # 2GB

# Recording limits
RECORDING_TIMEOUT = 3600  # 1 hour max
MIN_RECORDING_DURATION = 60  # 1 minute minimum

def create_directories():
    """Create required directories, skip if filesystem is read-only"""
    for directory in [TEMP_DIR, RECORDINGS_DIR, DOWNLOADS_DIR]:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"[Config] Directory created/verified: {directory}")
        except OSError as e:
            if e.errno == 30:  # Read-only file system
                print(f"[Config] Warning: Read-only filesystem for {directory}, using /tmp instead")
            else:
                print(f"[Config] Error creating {directory}: {e}")

create_directories()
