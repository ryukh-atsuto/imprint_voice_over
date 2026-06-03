import os
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

class AudioMixer:
    @staticmethod
    def mix_voice_with_bg(voice_path, bg_music_path, output_path, volume_reduction=-18):
        """
        Mixes the generated voice (from voice_path) with a background music track (bg_music_path).
        Lowers the background music volume by volume_reduction (in dB), loops the background music if
        it is shorter than the voice, crops the background music to match the voice length,
        and saves the mixed result to output_path.
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"Voice file not found at {voice_path}")
        if not os.path.exists(bg_music_path):
            raise FileNotFoundError(f"Background music file not found at {bg_music_path}")
            
        # Load audio segments
        voice = AudioSegment.from_file(voice_path)
        bg_music = AudioSegment.from_file(bg_music_path)
        
        # Lower background music volume so voice is prominent
        bg_music = bg_music + volume_reduction
        
        # Loop background music if it's shorter than the voice
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
