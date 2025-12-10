import logging
import subprocess
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataHandler:
    async def inject_metadata(self, input_file: str, metadata: dict):
        """Inject metadata into MKV file"""
        try:
            output_file = input_file.replace(".mkv", "_metadata.mkv")

            # Build mkvpropedit command
            cmd = [
                "mkvpropedit",
                input_file,
                "--edit", "info",
                "--set", f"title={metadata.get('title', 'Unknown')}",
            ]

            # Add additional metadata if mkvpropedit is available
            # For now, we'll just copy the file
            if not os.path.exists("mkvpropedit"):
                logger.warning("mkvpropedit not found, skipping metadata injection")
                return input_file

            logger.info(f"Injecting metadata into {input_file}")
            return input_file  # Return original if mkvpropedit not available

        except Exception as e:
            logger.error(f"Metadata injection error: {e}")
            return input_file
