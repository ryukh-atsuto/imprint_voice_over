import os
import sys
import numpy as np
from pydub import AudioSegment

# Dynamically add local ffmpeg to PATH so pydub can find it
ffmpeg_dirs = [
    r"C:\Users\User\AppData\Local\ffmpeg",
    r"C:\Users\User\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin"
]
for ffmpeg_dir in ffmpeg_dirs:
    if os.path.exists(ffmpeg_dir):
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            print("Added ffmpeg to PATH:", ffmpeg_dir)

def generate_chill_loop(duration_sec=30, sample_rate=44100):
    print("Generating chill lo-fi loop...")
    # Lofi chord progression: Cmaj7 - Am7 - Fmaj7 - G7
    chords = [
        [130.81, 164.81, 196.00, 246.94],  # Cmaj7 (low octave)
        [110.00, 130.81, 164.81, 196.00],  # Am7
        [87.31, 110.00, 130.81, 174.61],   # Fmaj7
        [98.00, 123.47, 146.83, 174.61]    # G7
    ]
    
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    # 4 chords, each playing for 3.75 seconds
    chord_duration = 3.75
    samples_per_chord = int(sample_rate * chord_duration)
    
    for i in range(4):
        chord = chords[i]
        chord_wave = np.zeros(samples_per_chord)
        for freq in chord:
            t = np.linspace(0, chord_duration, samples_per_chord, endpoint=False)
            wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.15 * np.sin(2 * np.pi * freq * 3 * t)
            chord_wave += wave
            
        # Add a very slow tremolo (LFO)
        lfo = 0.8 + 0.2 * np.sin(2 * np.pi * 1.5 * np.linspace(0, chord_duration, samples_per_chord))
        chord_wave *= lfo
        
        # Apply fade in/out for chord transition
        fade_len = int(sample_rate * 0.5)
        envelope = np.ones_like(chord_wave)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        
        start_idx = i * samples_per_chord
        data[start_idx:start_idx+samples_per_chord] = chord_wave * envelope * 0.2
        
    # Add a soft crackle (vinyl sound)
    crackle = np.random.normal(0, 0.004, total_samples)
    data += crackle
    
    # Add a slow, simple drum beat (kick on 1, snare on 3)
    beat_dur = 0.75  # 80 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        # Kick drum on beat 0 and 2 of every 4 beats
        if beat_idx % 4 == 0 or beat_idx % 4 == 2:
            kick_t = np.linspace(0, 0.15, int(sample_rate * 0.15), endpoint=False)
            freq_sweep = 120 * np.exp(-30 * kick_t)
            kick_wave = 0.5 * np.sin(2 * np.pi * np.cumsum(freq_sweep) / sample_rate)
            kick_wave *= np.exp(-15 * kick_t)
            data[start_sample:start_sample+len(kick_wave)] += kick_wave * 0.4
            
        # Snare drum on beat 1 and 3 of every 4 beats
        if beat_idx % 4 == 1 or beat_idx % 4 == 3:
            snare_len = int(sample_rate * 0.18)
            snare_t = np.linspace(0, 0.18, snare_len, endpoint=False)
            snare_noise = np.random.normal(0, 0.3, snare_len)
            snare_wave = snare_noise * np.exp(-12 * snare_t)
            data[start_sample:start_sample+snare_len] += snare_wave * 0.15

    return data, sample_rate

def generate_upbeat_loop(duration_sec=30, sample_rate=44100):
    print("Generating upbeat synth-pop/tech loop...")
    # Fast energetic chord progression: Am - F - C - G
    beat_dur = 0.5  # 120 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    bass_notes = [
        110.00, # A2
        87.31,  # F2
        130.81, # C3
        98.00   # G2
    ]
    
    bar_duration = 4.0
    samples_per_bar = int(sample_rate * bar_duration)
    
    for bar_idx in range(4):  # 4 bars total = 16 seconds
        bass_freq = bass_notes[bar_idx % len(bass_notes)]
        bar_start = bar_idx * samples_per_bar
        
        # Synthesize rhythmic driving bassline
        for beat in range(8):
            note_dur = 0.22
            note_samples = int(sample_rate * note_dur)
            t = np.linspace(0, note_dur, note_samples, endpoint=False)
            
            bass_wave = 0.4 * np.sin(2 * np.pi * bass_freq * t) + \
                        0.2 * np.sin(2 * np.pi * bass_freq * 2 * t) + \
                        0.1 * np.sin(2 * np.pi * bass_freq * 3 * t)
            
            envelope = np.exp(-10 * t)
            bass_wave *= envelope
            
            # First 8th note
            idx1 = bar_start + int(beat * samples_per_beat)
            if idx1 + note_samples < total_samples:
                data[idx1:idx1+note_samples] += bass_wave * 0.35
                
            # Second 8th note (off-beat)
            idx2 = bar_start + int((beat + 0.5) * samples_per_beat)
            if idx2 + note_samples < total_samples:
                data[idx2:idx2+note_samples] += bass_wave * 0.25
                
        # Synthesize pad chord playing in the background
        chord_freqs = {
            110.00: [220.00, 261.63, 329.63], # Am
            87.31: [174.61, 220.00, 261.63],  # F
            130.81: [261.63, 329.63, 392.00], # C
            98.00: [196.00, 246.94, 293.66]   # G
        }[bass_freq]
        
        pad_wave = np.zeros(samples_per_bar)
        for freq in chord_freqs:
            t_pad = np.linspace(0, bar_duration, samples_per_bar, endpoint=False)
            pad_wave += 0.5 * np.sin(2 * np.pi * freq * t_pad)
            
        # Subtle sidechain compression (volume dips on the kick beats)
        sc_env = 1.0 - 0.5 * np.abs(np.sin(2 * np.pi * np.linspace(0, bar_duration, samples_per_bar) * 2))
        pad_wave *= sc_env
        
        # Fade bar transitions
        fade_len = int(sample_rate * 0.1)
        env = np.ones_like(pad_wave)
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)
        
        if bar_start + samples_per_bar <= total_samples:
            data[bar_start:bar_start+samples_per_bar] += pad_wave * env * 0.12
            
    # Add heavy drum beat: Kick on every beat, Snare on 2 and 4
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        # Kick drum
        kick_t = np.linspace(0, 0.12, int(sample_rate * 0.12), endpoint=False)
        freq_sweep = 150 * np.exp(-35 * kick_t)
        kick_wave = np.sin(2 * np.pi * np.cumsum(freq_sweep) / sample_rate) * np.exp(-18 * kick_t)
        data[start_sample:start_sample+len(kick_wave)] += kick_wave * 0.5
        
        # Snare drum
        if beat_idx % 2 == 1:
            snare_len = int(sample_rate * 0.15)
            snare_t = np.linspace(0, 0.15, snare_len, endpoint=False)
            snare_noise = np.random.normal(0, 0.35, snare_len)
            snare_wave = snare_noise * np.exp(-15 * snare_t)
            data[start_sample:start_sample+snare_len] += snare_wave * 0.22
            
        # Hi-hat on off-beats
        hh_start = start_sample + int(samples_per_beat * 0.5)
        hh_len = int(sample_rate * 0.04)
        hh_t = np.linspace(0, 0.04, hh_len, endpoint=False)
        hh_noise = np.random.normal(0, 0.25, hh_len)
        hh_wave = hh_noise * np.exp(-60 * hh_t)
        if hh_start + hh_len < total_samples:
            data[hh_start:hh_start+hh_len] += hh_wave * 0.18

    return data, sample_rate

def save_to_mp3(data, sample_rate, filepath):
    # Normalize to prevent clipping
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data = data / max_val
        
    # Convert float64 to int16
    audio_int16 = (data * 32767).astype(np.int16)
    
    # Export using pydub
    audio_segment = AudioSegment(
        audio_int16.tobytes(), 
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    audio_segment.export(filepath, format="mp3", bitrate="192k")
    print(f"Saved {filepath}")

if __name__ == "__main__":
    static_audio_dir = "static/audio"
    
    chill_data, sr = generate_chill_loop(15)
    save_to_mp3(chill_data, sr, os.path.join(static_audio_dir, "chill.mp3"))
    
    upbeat_data, sr = generate_upbeat_loop(16)
    save_to_mp3(upbeat_data, sr, os.path.join(static_audio_dir, "upbeat.mp3"))
    print("Loops generation complete!")
