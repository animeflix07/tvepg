"""
Comprehensive setup verification script for JioTV Telegram Bot
Tests all components and configurations
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VerificationReport:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0

    def add_check(self, name: str, status: bool, details: str = ""):
        status_str = "✅ PASS" if status else "❌ FAIL"
        self.checks.append({
            "name": name,
            "status": status,
            "details": details
        })
        if status:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status_str} | {name}: {details}")

    def print_summary(self):
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total Checks: {len(self.checks)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/len(self.checks)*100):.1f}%")
        print("="*70)
        return self.failed == 0

def check_env_variables():
    """Check all required environment variables"""
    print("\n[1] CHECKING ENVIRONMENT VARIABLES")
    print("-" * 70)
    report = VerificationReport()

    required_vars = {
        "API_ID": "Telegram API ID",
        "API_HASH": "Telegram API Hash",
        "BOT_TOKEN": "Telegram Bot Token",
        "OWNER_ID": "Owner Telegram ID",
        "DB_URL": "MongoDB Connection URL",
        "DB_NAME": "MongoDB Database Name"
    }

    for var, description in required_vars.items():
        value = os.getenv(var, "")
        is_set = bool(value)

        if var == "BOT_TOKEN":
            is_valid = value.startswith("") and ":" in value
            report.add_check(var, is_set and is_valid,
                           f"{description} | Valid format: {is_valid}")
        elif var in ["API_ID", "OWNER_ID"]:
            is_valid = value.isdigit() if value else False
            report.add_check(var, is_set and is_valid,
                           f"{description} | Valid format: {is_valid}")
        else:
            report.add_check(var, is_set, description)

    return report

def check_directories():
    """Check if required directories exist/can be created"""
    print("\n[2] CHECKING DIRECTORIES")
    print("-" * 70)
    report = VerificationReport()

    dirs = {
        "TEMP_DIR": os.getenv("TEMP_DIR", "/tmp/jiotv_bot"),
        "RECORDINGS_DIR": os.getenv("RECORDINGS_DIR", "/data/recordings"),
        "DOWNLOADS_DIR": os.getenv("DOWNLOADS_DIR", "/data/downloads")
    }

    for dir_name, dir_path in dirs.items():
        try:
            os.makedirs(dir_path, exist_ok=True)
            is_writable = os.access(dir_path, os.W_OK)
            report.add_check(dir_name, is_writable, f"Path: {dir_path}")
        except Exception as e:
            report.add_check(dir_name, False, str(e))

    return report

def check_python_packages():
    """Check if all required Python packages are installed"""
    print("\n[3] CHECKING PYTHON PACKAGES")
    print("-" * 70)
    report = VerificationReport()

    required_packages = {
        "aiogram": "Telegram Bot Framework",
        "python-dotenv": "Environment Variable Loading",
        "pymongo": "MongoDB Driver",
        "motor": "Async MongoDB Driver",
        "requests": "HTTP Library",
        "aiofiles": "Async File Operations",
        "Pillow": "Image Processing"
    }

    for package, description in required_packages.items():
        try:
            __import__(package.replace("-", "_"))
            report.add_check(package, True, description)
        except ImportError:
            report.add_check(package, False, f"{description} - NOT INSTALLED")

    return report

async def check_mongodb_connection():
    """Check MongoDB connectivity"""
    print("\n[4] CHECKING MONGODB CONNECTION")
    print("-" * 70)
    report = VerificationReport()

    try:
        from motor.motor_asyncio import AsyncClient
        from config import MONGODB_URI, DB_NAME

        client = AsyncClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

        # Test connection
        await client.admin.command('ping')
        report.add_check("MongoDB Connection", True, f"Database: {DB_NAME}")

        # Check collections
        db = client[DB_NAME]
        collections_needed = ['users', 'premium', 'banned', 'config', 'recordings']

        existing = await db.list_collection_names()
        for coll in collections_needed:
            exists = coll in existing
            report.add_check(f"Collection '{coll}'", exists,
                           "Exists" if exists else "Missing (will be created)")

        await client.close()
    except Exception as e:
        report.add_check("MongoDB Connection", False, str(e))

    return report

async def check_bot_token():
    """Check if bot token is valid"""
    print("\n[5] CHECKING BOT TOKEN")
    print("-" * 70)
    report = VerificationReport()

    try:
        from aiogram import Bot
        from config import BOT_TOKEN

        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()

        report.add_check("Bot Token Valid", True,
                       f"Bot: @{me.username} (ID: {me.id})")
        report.add_check("Bot First Name", True, me.first_name)
        report.add_check("Bot is User", not me.is_bot, "Should be bot" if me.is_bot else "Verified")

        await bot.session.close()
    except Exception as e:
        report.add_check("Bot Token Valid", False, str(e))

    return report

async def check_ffmpeg():
    """Check FFmpeg installation"""
    print("\n[6] CHECKING FFMPEG INSTALLATION")
    print("-" * 70)
    report = VerificationReport()

    try:
        import subprocess
        from config import FFMPEG_PATH, MKVMERGE_PATH

        # Check FFmpeg
        result = subprocess.run([FFMPEG_PATH, "-version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            report.add_check("FFmpeg", True, version_line[:50])
        else:
            report.add_check("FFmpeg", False, "Not found or not executable")

        # Check MKVMerge
        result = subprocess.run([MKVMERGE_PATH, "--version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            report.add_check("MKVMerge", True, version_line[:50])
        else:
            report.add_check("MKVMerge", False, "Not found or not executable")
    except Exception as e:
        report.add_check("FFmpeg/MKVMerge", False, str(e))

    return report

def check_bot_files():
    """Check if all bot files exist"""
    print("\n[7] CHECKING BOT FILES")
    print("-" * 70)
    report = VerificationReport()

    required_files = {
        "app.py": "Main bot entry",
        "config.py": "Configuration",
        "requirements.txt": "Dependencies",
        "database/db.py": "Database connection",
        "database/models.py": "Database models",
        "middlewares/access_control.py": "Access control middleware",
        "handlers/start.py": "Start handler",
        "handlers/auth.py": "Authentication handler",
        "handlers/admin.py": "Admin handler",
        "utils/jiotv_wrapper.py": "JioTV wrapper"
    }

    for file_path, description in required_files.items():
        exists = os.path.isfile(file_path)
        report.add_check(file_path, exists, description)

    return report

async def run_all_checks():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("JIOTV TELEGRAM BOT - SETUP VERIFICATION")
    print("="*70)

    # Synchronous checks
    env_report = check_env_variables()
    dir_report = check_directories()
    pkg_report = check_python_packages()
    file_report = check_bot_files()

    # Async checks
    mongo_report = await check_mongodb_connection()
    token_report = await check_bot_token()
    ffmpeg_report = await check_ffmpeg()

    # Final summary
    print("\n" + "="*70)
    print("OVERALL STATUS")
    print("="*70)

    all_reports = [env_report, dir_report, pkg_report, file_report,
                   mongo_report, token_report, ffmpeg_report]

    total_passed = sum(r.passed for r in all_reports)
    total_failed = sum(r.failed for r in all_reports)
    total_checks = sum(len(r.checks) for r in all_reports)

    print(f"Total Checks: {total_checks}")
    print(f"Passed: {total_passed} ✅")
    print(f"Failed: {total_failed} ❌")
    print(f"Success Rate: {(total_passed/total_checks*100):.1f}%")
    print("="*70)

    if total_failed == 0:
        print("\n🎉 ALL CHECKS PASSED! Bot is ready to run.\n")
        return 0
    else:
        print(f"\n⚠️  {total_failed} check(s) failed. Please fix the issues above.\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_checks())
    sys.exit(exit_code)
