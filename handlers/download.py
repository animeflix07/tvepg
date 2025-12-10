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

@router.message(Command("dl"))
async def download_command(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Only owner can download.")
        return

    # Parse: /dl -c <channel> -d <DD-MM-YYYY> -t <start_time> - <end_time>
    text = message.text

    try:
        # Extract parameters
        channel = extract_param(text, "-c")
        date = extract_param(text, "-d")
        times = extract_times(text, "-t")

        if not all([channel, date, times]):
            await message.answer("Usage: /dl -c <channel> -d <DD-MM-YYYY> -t <start_time> - <end_time>")
            return

        status_msg = await message.answer(f"📥 Downloading {channel} for {date} ({times[0]} - {times[1]})...")

        jio = JioTVWrapper()
        stream_url = await jio.get_catchup_url(channel, date, times[0], times[1])

        if not stream_url:
            await status_msg.edit_text("❌ Could not get stream URL")
            return

        recording_id = str(uuid.uuid4())
        start_dt = datetime.strptime(f"{date} {times[0]}", "%d-%m-%Y %H:%M")
        end_dt = datetime.strptime(f"{date} {times[1]}", "%d-%m-%Y %H:%M")

        await Database.create_recording(
            recording_id,
            message.from_user.id,
            channel,
            channel,
            start_dt,
            end_dt
        )

        # Download
        ffmpeg = FFmpegHandler()
        duration = int((end_dt - start_dt).total_seconds())

        output_file = await ffmpeg.download_stream(
            stream_url,
            channel,
            duration,
            {"quality": "720p", "audio_tracks": ["hindi"]}
        )

        if not output_file:
            await status_msg.edit_text("❌ Download failed")
            return

        await status_msg.edit_text("⚙️ Processing metadata...")

        # Inject metadata
        metadata_handler = MetadataHandler()
        final_file = await metadata_handler.inject_metadata(
            output_file,
            {
                "title": channel,
                "date": date,
                "start_time": times[0],
                "end_time": times[1],
                "quality": "720p",
                "audio_tracks": ["hindi"],
                "codec": "H.264",
                "audio_codec": "AAC"
            }
        )

        await status_msg.edit_text("📤 Uploading to Telegram...")

        caption = f"📺 Channel: {channel}\n📅 Date: {date}\n⏱ Duration: {times[0]} - {times[1]}\n🎞 Quality: 720p\n📦 Source: JioTV WEB-DL"

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
        await message.answer("✅ Download completed!")

    except Exception as e:
        logger.error(f"Download error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

def extract_param(text: str, param: str) -> str:
    try:
        idx = text.find(param)
        if idx == -1:
            return None
        start = idx + len(param) + 1
        end = text.find(" -", start)
        if end == -1:
            end = len(text)
        return text[start:end].strip()
    except:
        return None

def extract_times(text: str, param: str):
    try:
        idx = text.find(param)
        if idx == -1:
            return None
        start = idx + len(param) + 1
        times_str = text[start:].strip()
        parts = times_str.split(" - ")
        if len(parts) == 2:
            return [parts[0].strip(), parts[1].strip()]
        return None
    except:
        return None
