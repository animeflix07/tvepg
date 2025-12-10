from datetime import datetime
from utils.language_mapper import map_languages

def generate_filename(channel_name: str, duration: int, metadata: dict) -> str:
    """
    Generate filename in format:
    channel.name.[DD-MM-YYYY].[HH.MM-HH.MM].quality.JioTV.WEB-DL.langs.AAC.2.0.H264-Madara2718.mkv
    """
    # Replace spaces with dots
    channel_formatted = channel_name.replace(" ", ".")

    # Date in DD-MM-YYYY format
    date_str = datetime.now().strftime("%d-%m-%Y")

    # Time (simplified to just current time - adjust as needed)
    start_time = "00.00"
    end_time = f"{(duration // 3600):02d}.{((duration % 3600) // 60):02d}"
    time_str = f"{start_time}-{end_time}"

    # Quality
    quality = metadata.get("quality", "720p")

    # Languages
    audio_tracks = metadata.get("audio_tracks", ["hindi"])
    langs = map_languages(audio_tracks)
    langs_str = "-".join(langs)

    # Build filename
    filename = f"{channel_formatted}.[{date_str}].[{time_str}].{quality}.JioTV.WEB-DL.{langs_str}.AAC.2.0.H264-Madara2718.mkv"

    return filename
