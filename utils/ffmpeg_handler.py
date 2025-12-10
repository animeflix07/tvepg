import logging
import subprocess
import os
from datetime import datetime
from config import FFMPEG_PATH, TEMP_DIR, DOWNLOADS_DIR as OUTPUT_DIR
from utils.filename_generator import generate_filename

logger = logging.getLogger(__name__)

class FFmpegHandler:
    def __init__(self):
        self.ffmpeg_path = FFMPEG_PATH
        self.temp_dir = TEMP_DIR
        self.output_dir = OUTPUT_DIR

    async def record_stream(self, stream_url: str, channel_name: str, duration: int, metadata: dict):
        """Record live stream"""
        try:
            filename = generate_filename(channel_name, duration, metadata)
            output_path = os.path.join(self.output_dir, filename)

            cmd = [
                self.ffmpeg_path,
                "-i", stream_url,
                "-t", str(duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ]

            logger.info(f"Starting recording: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                return None

            logger.info(f"Recording completed: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Record stream error: {e}")
            return None

    async def download_stream(self, stream_url: str, channel_name: str, duration: int, metadata: dict):
        """Download stream"""
        try:
            filename = generate_filename(channel_name, duration, metadata)
            output_path = os.path.join(self.output_dir, filename)

            cmd = [
                self.ffmpeg_path,
                "-i", stream_url,
                "-t", str(duration),
                "-c:v", "libx264",
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ]

            logger.info(f"Starting download: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                return None

            logger.info(f"Download completed: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Download stream error: {e}")
            return None
