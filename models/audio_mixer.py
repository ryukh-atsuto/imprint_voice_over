import os
import math
from pydub import AudioSegment

# Dynamically add local ffmpeg to PATH so pydub can find it
ffmpeg_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')),
    r"F:\text_to_voice\bin"
]
for ffmpeg_dir in ffmpeg_dirs:
    if os.path.exists(ffmpeg_dir):
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            print("[AudioMixer] Added ffmpeg to PATH:", ffmpeg_dir)

# Explicitly configure AudioSegment paths for maximum reliability on Windows
AudioSegment.converter = r"F:\text_to_voice\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"F:\text_to_voice\bin\ffprobe.exe"


class AudioMixer:
    @staticmethod
    def pct_to_db(pct):
        """Converts percentage volume (0-100) to decibels gain."""
        if pct <= 0:
            return -100
        # 100% -> 0dB, 50% -> -6dB, 10% -> -20dB, etc.
        return 20 * math.log10(pct / 100.0)

    @classmethod
    def mix_voice_with_bg(cls, voice_path, bg_music_path, output_path, voice_vol_pct=100, bg_vol_pct=40, ducking_threshold=15):
        """
        Mixes voice and background music using percentage volumes and ducking.
        - voice_vol_pct: 0-100% volume for the voice.
        - bg_vol_pct: 0-100% volume for the background.
        - ducking_threshold: additional dB reduction for background music when mixed.
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"Voice file not found at {voice_path}")
        if not os.path.exists(bg_music_path):
            raise FileNotFoundError(f"Background music file not found at {bg_music_path}")
            
        # Load audio segments
        voice = AudioSegment.from_file(voice_path)
        bg_music = AudioSegment.from_file(bg_music_path)
        
        # Apply voice volume adjustment
        voice_db = cls.pct_to_db(voice_vol_pct)
        if voice_db > -100:
            voice = voice + voice_db
        else:
            voice = voice - 100  # Silence
            
        # Apply background music volume adjustment (with ducking reduction)
        # Higher ducking_threshold = background is ducked further down relative to voice
        total_bg_reduction_db = cls.pct_to_db(bg_vol_pct) - ducking_threshold
        if total_bg_reduction_db > -100:
            bg_music = bg_music + total_bg_reduction_db
        else:
            bg_music = bg_music - 100
            
        # Loop background music if it is shorter than the voice
        voice_len = len(voice)
        bg_len = len(bg_music)
        
        if bg_len < voice_len:
            loops_needed = (voice_len // bg_len) + 1
            bg_music = bg_music * loops_needed
            
        # Trim background music to match voice duration exactly
        bg_music = bg_music[:voice_len]
        
        # Add a subtle fade-out to background music (e.g. 500ms)
        bg_music = bg_music.fade_out(500)
        
        # Overlay voice onto background music
        mixed = bg_music.overlay(voice)
        
        # Export as MP3
        mixed.export(output_path, format="mp3")
        print(f"[AudioMixer] Successfully mixed audio and saved to {output_path}")
        return output_path
