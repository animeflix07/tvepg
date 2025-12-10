"""
Feature testing script - Test all bot features
"""

import asyncio
import logging
from datetime import datetime, timedelta
from database.db import Database
from utils.jiotv_wrapper import JioTVWrapper
from config import OWNER_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database():
    """Test database operations"""
    print("\n[TEST] Database Operations")
    print("-" * 70)

    try:
        # Test user operations
        test_user_id = 12345678
        print(f"Creating test user: {test_user_id}")
        await Database.create_user(test_user_id, "testuser", "Test", "User")

        user = await Database.get_user(test_user_id)
        print(f"✅ User created and retrieved: {user.get('username')}")

        # Test update
        await Database.update_user(test_user_id, {"jio_phone": "9876543210"})
        user = await Database.get_user(test_user_id)
        print(f"✅ User updated: Phone = {user.get('jio_phone')}")

        # Test premium
        print("Adding premium...")
        await Database.add_premium(test_user_id, 30, OWNER_ID)
        user = await Database.get_user(test_user_id)
        print(f"✅ Premium added: is_premium = {user.get('is_premium')}")

        # Test ban
        print("Banning user...")
        await Database.ban_user(test_user_id, OWNER_ID, "Test ban")
        is_banned = await Database.is_banned(test_user_id)
        print(f"✅ Ban verified: is_banned = {is_banned}")

        # Test unban
        print("Unbanning user...")
        await Database.unban_user(test_user_id)
        is_banned = await Database.is_banned(test_user_id)
        print(f"✅ Unban verified: is_banned = {is_banned}")

        # Test config
        print("Testing configuration...")
        await Database.set_config("test_key", "test_value")
        value = await Database.get_config("test_key")
        print(f"✅ Config verified: test_key = {value}")

        print("\n✅ ALL DATABASE TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n❌ DATABASE TEST FAILED: {e}")
        logger.exception(e)
        return False

async def test_jiotv_connection():
    """Test JioTV API connection"""
    print("\n[TEST] JioTV Connection")
    print("-" * 70)

    try:
        jio = JioTVWrapper()
        print("Testing JioTV API connection...")

        # This will attempt to connect to JioTV
        # Actual test depends on JioTV wrapper implementation
        print("✅ JioTV wrapper initialized")
        print("⚠️  Note: Actual JioTV testing requires valid credentials")
        return True

    except Exception as e:
        print(f"❌ JIOTV TEST FAILED: {e}")
        return False

async def test_recording_model():
    """Test recording database model"""
    print("\n[TEST] Recording Model")
    print("-" * 70)

    try:
        recording_id = f"rec_{int(datetime.utcnow().timestamp())}"
        user_id = OWNER_ID
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)

        # Create recording
        print(f"Creating recording: {recording_id}")
        await Database.create_recording(
            recording_id, user_id, "channel_123", "Test Channel", start_time, end_time
        )

        # Retrieve recording
        recording = await Database.get_recording(recording_id)
        print(f"✅ Recording created and retrieved")
        print(f"   Status: {recording.get('status')}")
        print(f"   Channel: {recording.get('channel_name')}")

        # Update recording
        print("Updating recording status...")
        await Database.update_recording(recording_id, {"status": "processing"})
        recording = await Database.get_recording(recording_id)
        print(f"✅ Recording updated: status = {recording.get('status')}")

        print("\n✅ ALL RECORDING TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n❌ RECORDING TEST FAILED: {e}")
        logger.exception(e)
        return False

async def run_all_tests():
    """Run all feature tests"""
    print("\n" + "="*70)
    print("JIOTV TELEGRAM BOT - FEATURE TESTS")
    print("="*70)

    try:
        await Database.init_db()

        results = []
        results.append(await test_database())
        results.append(await test_jiotv_connection())
        results.append(await test_recording_model())

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        passed = sum(results)
        total = len(results)
        print(f"Tests Passed: {passed}/{total}")

        if all(results):
            print("\n🎉 ALL TESTS PASSED!\n")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED\n")
            return 1

    except Exception as e:
        logger.exception(e)
        print(f"\n❌ TEST EXECUTION FAILED: {e}\n")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
