import logging
import uuid
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from config import OWNER_ID
from database.db import Database
from utils.jiotv_wrapper import JioTVWrapper
from utils.ffmpeg_handler import FFmpegHandler
from utils.metadata_handler import MetadataHandler
from utils.caption_builder import build_caption

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("record"))
async def record_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can record.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /record <channel_name> <HH:MM:SS>")
        return

    channel_name = args[1]
    duration_str = args[2]

    try:
        # Parse duration
        parts = duration_str.split(":")
        if len(parts) != 3:
            await message.answer("Duration format: HH:MM:SS")
            return

        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        total_seconds = hours * 3600 + minutes * 60 + seconds

        # Get stream URL
        jio = JioTVWrapper()
        stream_info = await jio.get_stream_url(channel_name)

        if not stream_info:
            await message.answer(f"❌ Could not get stream for {channel_name}")
            return

        recording_id = str(uuid.uuid4())

        # Create recording record
        await Database.create_recording(
            recording_id,
            message.from_user.id,
            stream_info.get("channel_id"),
            channel_name,
            datetime.utcnow(),
            datetime.utcnow()
        )

        status_msg = await message.answer(f"🔴 Recording {channel_name} for {duration_str}...")

        # Start recording
        ffmpeg = FFmpegHandler()
        output_file = await ffmpeg.record_stream(
            stream_info.get("url"),
            channel_name,
            total_seconds,
            stream_info
        )

        if not output_file:
            await Database.update_recording(recording_id, {"status": "failed"})
            await status_msg.edit_text("❌ Recording failed")
            return

        # Inject metadata
        metadata_handler = MetadataHandler()
        final_file = await metadata_handler.inject_metadata(
            output_file,
            {
                "title": channel_name,
                "date": datetime.now().strftime("%d-%m-%Y"),
                "duration": duration_str,
                "quality": stream_info.get("quality", "unknown"),
                "audio_tracks": stream_info.get("audio_tracks", []),
                "codec": stream_info.get("codec", "H.264"),
                "audio_codec": stream_info.get("audio_codec", "AAC")
            }
        )

        # Upload to Telegram
        await status_msg.edit_text("📤 Uploading to Telegram...")

        caption = build_caption(channel_name, duration_str, stream_info)

        with open(final_file, "rb") as video_file:
            sent_message = await message.answer_video(
                video=video_file,
                caption=caption,
                supports_streaming=True
            )

        await Database.update_recording(
            recording_id,
            {
                "status": "completed",
                "output_file": final_file,
                "message_id": sent_message.message_id
            }
        )

        await status_msg.delete()
        await message.answer("✅ Recording completed and uploaded!")

    except Exception as e:
        logger.error(f"Recording error: {e}")
        await message.answer(f"❌ Error: {str(e)}")
