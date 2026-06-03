import os
os.environ["HF_HOME"] = r"F:\huggingface_cache"

import torch
import numpy as np
import scipy.io.wavfile as wavfile
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
            print("[TTSEngine] Added ffmpeg to PATH:", ffmpeg_dir)

class TTSEngine:
    def __init__(self):
        # Determine device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
            
        print(f"[TTSEngine] Initialized on device: {self.device}")
        
        # Cache models to avoid reloading
        self._models = {}
        
    def generate_bark(self, text, output_path):
        """
        IF Language = English AND Engine = "Bark (Expressive, Slow)"
        Uses suno/bark-small model to generate expressive speech.
        """
        from transformers import AutoProcessor, BarkModel
        
        model_id = "suno/bark-small"
        
        if model_id not in self._models:
            print(f"[TTSEngine] Loading {model_id}...")
            processor = AutoProcessor.from_pretrained(model_id)
            model = BarkModel.from_pretrained(model_id).to(self.device)
            self._models[model_id] = (processor, model)
        else:
            processor, model = self._models[model_id]
            
        # Standard speaker preset
        voice_preset = "v2/en_speaker_6"
        inputs = processor(text=text, voice_preset=voice_preset).to(self.device)
        
        print("[TTSEngine] Generating Bark speech...")
        with torch.no_grad():
            audio_array = model.generate(**inputs)
            
        # Convert to numpy and squeeze
        audio_array = audio_array.cpu().numpy().squeeze()
        
        # Normalise to prevent clipping
        if np.max(np.abs(audio_array)) > 0:
            audio_array = audio_array / np.max(np.abs(audio_array))
            
        sample_rate = 24000
        audio_int16 = (audio_array * 32767).astype(np.int16)
        
        # Convert to MP3
        audio_segment = AudioSegment(
            audio_int16.tobytes(), 
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        audio_segment.export(output_path, format="mp3")
        print(f"[TTSEngine] Saved Bark audio to {output_path}")
        return output_path

    def generate_kokoro(self, text, output_path, voice="af_heart", background_vibe="none"):
        """
        IF Language = English AND Engine = "Kokoro (Ultra-Fast Voice + Background Music)"
        Uses fastrtc/kokoro-onnx model weights via kokoro-onnx library and overlays background vibe.
        """
        from kokoro_onnx import Kokoro
        from huggingface_hub import hf_hub_download
        
        model_key = "kokoro_onnx_model"
        if model_key not in self._models:
            print("[TTSEngine] Downloading Kokoro ONNX model and voices...")
            model_path = hf_hub_download(repo_id="fastrtc/kokoro-onnx", filename="kokoro-v1.0.onnx")
            voices_path = hf_hub_download(repo_id="fastrtc/kokoro-onnx", filename="voices-v1.0.bin")
            print("[TTSEngine] Loading Kokoro ONNX session...")
            self._models[model_key] = Kokoro(model_path, voices_path)
            
        kokoro = self._models[model_key]
        
        # Select correct language code for Kokoro
        lang = "en-us"
        if voice.startswith("bf_") or voice.startswith("bm_"):
            lang = "en-gb"
            
        print(f"[TTSEngine] Generating Kokoro speech with voice {voice} (lang: {lang})...")
        samples, sample_rate = kokoro.create(
            text,
            voice=voice,
            speed=1.0,
            lang=lang
        )
        
        # Normalise to prevent clipping
        if np.max(np.abs(samples)) > 0:
            samples = samples / np.max(np.abs(samples))
            
        audio_int16 = (samples * 32767).astype(np.int16)
        
        audio_segment = AudioSegment(
            audio_int16.tobytes(), 
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        
        # Handle Background Music Overlaying
        loop_path = os.path.join("static", "audio", f"{background_vibe}.mp3")
        if background_vibe != "none" and os.path.exists(loop_path):
            print(f"[TTSEngine] Mixing in background vibe: {background_vibe}...")
            loop_segment = AudioSegment.from_file(loop_path)
            
            # Reduce volume of background loop (-20dB) so voice is crisp and audible
            loop_segment = loop_segment - 20
            
            # Overlay speech segment on looped backing track
            mixed_segment = loop_segment.overlay(audio_segment, position=0, loop=True)
            
            # Trim mixed audio to speech length + 1 second padding
            mixed_segment = mixed_segment[:len(audio_segment) + 1000]
            
            # Apply a 1-second fade out at the end
            mixed_segment = mixed_segment.fade_out(1000)
            
            mixed_segment.export(output_path, format="mp3")
            print(f"[TTSEngine] Saved mixed Kokoro audio + loop to {output_path}")
        else:
            audio_segment.export(output_path, format="mp3")
            print(f"[TTSEngine] Saved voice-only Kokoro audio to {output_path}")
            
        return output_path

    def generate_mms_bangla(self, text, output_path):
        """
        IF Language = Bangla AND Engine = "Meta MMS / Indic-TTS (Native Bangla Speed)"
        Uses facebook/mms-tts-ben to generate native Bangla audio speech.
        """
        from transformers import VitsModel, AutoTokenizer
        
        model_id = "facebook/mms-tts-ben"
        
        if model_id not in self._models:
            print(f"[TTSEngine] Loading {model_id}...")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = VitsModel.from_pretrained(model_id).to(self.device)
            self._models[model_id] = (tokenizer, model)
        else:
            tokenizer, model = self._models[model_id]
            
        inputs = tokenizer(text, return_tensors="pt").to(self.device)
        
        print("[TTSEngine] Generating Meta MMS Bangla speech...")
        with torch.no_grad():
            output = model(**inputs).waveform
            
        audio_array = output.cpu().numpy().squeeze()
        sample_rate = model.config.sampling_rate
        
        # Normalise to prevent clipping
        if np.max(np.abs(audio_array)) > 0:
            audio_array = audio_array / np.max(np.abs(audio_array))
            
        audio_int16 = (audio_array * 32767).astype(np.int16)
        
        audio_segment = AudioSegment(
            audio_int16.tobytes(), 
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        audio_segment.export(output_path, format="mp3")
        print(f"[TTSEngine] Saved MMS Bangla audio to {output_path}")
        return output_path
