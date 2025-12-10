def build_caption(channel_name: str, duration: str, stream_info: dict) -> str:
    """Build caption for uploaded video"""
    audio_tracks = stream_info.get("audio_tracks", ["Hindi"])
    audio_codec = stream_info.get("audio_codec", "AAC")
    video_codec = stream_info.get("codec", "H.264")
    quality = stream_info.get("quality", "720p")

    caption = f"""📺 Channel: {channel_name}
📅 Date: {__import__('datetime').datetime.now().strftime('%d-%m-%Y')}
⏱ Duration: {duration}
🎞 Quality: {quality}
🔊 Audio: {', '.join(audio_tracks)}
🎧 Audio Codec: {audio_codec}
🎥 Video Codec: {video_codec}
📦 Source: JioTV WEB-DL
🧑‍💻 Encoded By: Madara2718"""

    return caption
