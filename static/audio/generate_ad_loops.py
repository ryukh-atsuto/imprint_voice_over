import os
import sys
import numpy as np
from pydub import AudioSegment

# Dynamically add local ffmpeg to PATH so pydub can find it
ffmpeg_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bin')),
    r"F:\text_to_voice\bin"
]
for ffmpeg_dir in ffmpeg_dirs:
    if os.path.exists(ffmpeg_dir):
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            print("Added ffmpeg to PATH:", ffmpeg_dir)

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

def generate_upbeat_pop(duration_sec=15, sample_rate=44100):
    print("Generating Upbeat Pop loop...")
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    # Progression: C - G - Am - F
    chord_freqs = [
        [130.81, 164.81, 196.00],  # C Major
        [98.00, 146.83, 196.00],   # G Major
        [110.00, 130.81, 164.81],  # A Minor
        [87.31, 130.81, 174.61]    # F Major
    ]
    
    chord_duration = duration_sec / 4.0
    samples_per_chord = int(sample_rate * chord_duration)
    
    for i in range(4):
        chord = chord_freqs[i]
        chord_wave = np.zeros(samples_per_chord)
        for freq in chord:
            t = np.linspace(0, chord_duration, samples_per_chord, endpoint=False)
            wave = 0.5 * np.sin(2 * np.pi * freq * t) + 0.15 * np.sin(2 * np.pi * freq * 2 * t)
            chord_wave += wave
            
        # Add simple rhythmic pulse (8th note sidechain feel)
        sc = 0.8 + 0.2 * np.sin(2 * np.pi * 4 * np.linspace(0, chord_duration, samples_per_chord))
        chord_wave *= sc
        
        fade_len = int(sample_rate * 0.1)
        envelope = np.ones_like(chord_wave)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        
        start_idx = i * samples_per_chord
        data[start_idx:start_idx+samples_per_chord] = chord_wave * envelope * 0.18
        
    # Standard pop drum beat
    beat_dur = 0.5  # 120 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        # Kick
        kick_t = np.linspace(0, 0.1, int(sample_rate * 0.1), endpoint=False)
        kick_freq = 150 * np.exp(-40 * kick_t)
        kick_wave = np.sin(2 * np.pi * np.cumsum(kick_freq) / sample_rate) * np.exp(-15 * kick_t)
        data[start_sample:start_sample+len(kick_wave)] += kick_wave * 0.4
        
        # Snare
        if beat_idx % 2 == 1:
            snare_len = int(sample_rate * 0.15)
            snare_t = np.linspace(0, 0.15, snare_len, endpoint=False)
            snare_noise = np.random.normal(0, 0.25, snare_len)
            snare_wave = snare_noise * np.exp(-18 * snare_t)
            data[start_sample:start_sample+snare_len] += snare_wave * 0.2
            
    return data, sample_rate

def generate_corporate_luxury(duration_sec=16, sample_rate=44100):
    print("Generating Corporate Luxury loop...")
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    # Smooth progression: Fmaj7 - G - Em7 - Am7
    chords = [
        [87.31, 130.81, 174.61, 220.00],  # Fmaj7
        [98.00, 146.83, 196.00, 246.94],   # G Major
        [82.41, 130.81, 164.81, 196.00],   # Em7
        [110.00, 164.81, 196.00, 261.63]   # Am7
    ]
    
    chord_duration = duration_sec / 4.0
    samples_per_chord = int(sample_rate * chord_duration)
    
    for i in range(4):
        chord = chords[i]
        chord_wave = np.zeros(samples_per_chord)
        for freq in chord:
            t = np.linspace(0, chord_duration, samples_per_chord, endpoint=False)
            # Pure, clean sine waves with 3rd harmonics for premium "glassy" Rhodes tone
            wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.1 * np.sin(2 * np.pi * freq * 3 * t)
            chord_wave += wave
            
        # Gentle tremolo LFO (4Hz)
        lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 4 * np.linspace(0, chord_duration, samples_per_chord))
        chord_wave *= lfo
        
        fade_len = int(sample_rate * 0.3)
        envelope = np.ones_like(chord_wave)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        
        start_idx = i * samples_per_chord
        data[start_idx:start_idx+samples_per_chord] = chord_wave * envelope * 0.15

    # Gentle jazzy beat (chill-out vibe)
    beat_dur = 0.705  # ~85 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        # Kick on 1
        if beat_idx % 2 == 0:
            kick_t = np.linspace(0, 0.12, int(sample_rate * 0.12), endpoint=False)
            kick_freq = 110 * np.exp(-30 * kick_t)
            kick_wave = np.sin(2 * np.pi * np.cumsum(kick_freq) / sample_rate) * np.exp(-12 * kick_t)
            data[start_sample:start_sample+len(kick_wave)] += kick_wave * 0.25
            
        # Soft rimshot on 2
        if beat_idx % 2 == 1:
            rim_len = int(sample_rate * 0.05)
            rim_t = np.linspace(0, 0.05, rim_len, endpoint=False)
            rim_wave = np.sin(2 * np.pi * 1200 * rim_t) * np.exp(-50 * rim_t)
            data[start_sample:start_sample+rim_len] += rim_wave * 0.08
            
    return data, sample_rate

def generate_electronic_loop(duration_sec=15, sample_rate=44100):
    print("Generating Electronic loop...")
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    # Rhythmic arpeggiator synth bass (driving house/techno)
    beat_dur = 0.48  # 125 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    
    # Bassline notes
    notes = [110.00, 110.00, 130.81, 98.00, 87.31, 87.31, 98.00, 110.00]
    
    for i in range(len(notes)):
        note_freq = notes[i]
        start_idx = i * samples_per_beat
        if start_idx + samples_per_beat > total_samples:
            break
            
        # Arpeggiate 8th notes
        for pulse in range(2):
            pulse_dur = beat_dur / 2.0
            pulse_samples = int(sample_rate * pulse_dur)
            t = np.linspace(0, pulse_dur, pulse_samples, endpoint=False)
            
            # Sawtooth-like wave
            bass = 0.3 * np.sin(2 * np.pi * note_freq * t) + \
                   0.15 * np.sin(2 * np.pi * note_freq * 2 * t) + \
                   0.08 * np.sin(2 * np.pi * note_freq * 4 * t)
                   
            # Exponential decay envelope (pluck sound)
            env = np.exp(-12 * t)
            
            p_start = start_idx + int(pulse * pulse_samples)
            if p_start + pulse_samples < total_samples:
                data[p_start:p_start+pulse_samples] += bass * env * 0.28
                
    # Four-on-the-floor kick beat
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        # Kick (heavy sub kick)
        kick_t = np.linspace(0, 0.12, int(sample_rate * 0.12), endpoint=False)
        kick_freq = 180 * np.exp(-45 * kick_t)
        kick_wave = np.sin(2 * np.pi * np.cumsum(kick_freq) / sample_rate) * np.exp(-16 * kick_t)
        data[start_sample:start_sample+len(kick_wave)] += kick_wave * 0.48
        
        # Offbeat open hi-hat
        hh_start = start_sample + int(samples_per_beat * 0.5)
        hh_len = int(sample_rate * 0.08)
        hh_t = np.linspace(0, 0.08, hh_len, endpoint=False)
        hh_noise = np.random.normal(0, 0.3, hh_len)
        hh_wave = hh_noise * np.exp(-25 * hh_t)
        if hh_start + hh_len < total_samples:
            data[hh_start:hh_start+hh_len] += hh_wave * 0.12
            
    return data, sample_rate

def generate_dramatic_cinematic(duration_sec=16, sample_rate=44100):
    print("Generating Dramatic Cinematic loop...")
    total_samples = sample_rate * duration_sec
    data = np.zeros(total_samples)
    
    # Epic brass & strings chord progression (Minor theme): Am - F - Dm - E
    chords = [
        [55.00, 110.00, 130.81, 164.81],  # Am (low, heavy)
        [43.65, 87.31, 130.81, 174.61],   # F
        [58.27, 116.54, 146.83, 174.61],  # Dm
        [41.20, 82.41, 123.47, 164.81]    # E
    ]
    
    chord_duration = duration_sec / 4.0
    samples_per_chord = int(sample_rate * chord_duration)
    
    for i in range(4):
        chord = chords[i]
        chord_wave = np.zeros(samples_per_chord)
        for freq in chord:
            t = np.linspace(0, chord_duration, samples_per_chord, endpoint=False)
            # Warm brass/string pad sound (sine + rich odd harmonics + detuning simulation)
            wave = 0.5 * np.sin(2 * np.pi * freq * t) + \
                   0.12 * np.sin(2 * np.pi * freq * 1.005 * t) + \
                   0.12 * np.sin(2 * np.pi * freq * 0.995 * t) + \
                   0.08 * np.sin(2 * np.pi * freq * 3 * t)
            chord_wave += wave
            
        # Slow cinematic swelling envelope
        fade_in = int(samples_per_chord * 0.3)
        fade_out = int(samples_per_chord * 0.3)
        envelope = np.ones_like(chord_wave)
        envelope[:fade_in] = np.linspace(0, 1, fade_in)
        envelope[-fade_out:] = np.linspace(1, 0, fade_out)
        
        start_idx = i * samples_per_chord
        data[start_idx:start_idx+samples_per_chord] = chord_wave * envelope * 0.22
        
    # Epic cinematic impact (Taiko/Tom hits on 1 and 3 of every 4 beats)
    beat_dur = 0.666  # 90 BPM
    samples_per_beat = int(sample_rate * beat_dur)
    
    for beat_idx in range(int(duration_sec / beat_dur)):
        start_sample = beat_idx * samples_per_beat
        if start_sample + samples_per_beat > total_samples:
            break
            
        if beat_idx % 4 == 0 or beat_idx % 4 == 2:
            impact_t = np.linspace(0, 0.4, int(sample_rate * 0.4), endpoint=False)
            # Low frequency thud
            impact_freq = 60 * np.exp(-12 * impact_t)
            impact_wave = np.sin(2 * np.pi * np.cumsum(impact_freq) / sample_rate) * np.exp(-6 * impact_t)
            
            # High frequency splash/reverb simulation using filtered noise
            noise = np.random.normal(0, 0.12, len(impact_t)) * np.exp(-25 * impact_t)
            
            full_impact = impact_wave + noise
            data[start_sample:start_sample+len(full_impact)] += full_impact * 0.55
            
    return data, sample_rate

if __name__ == "__main__":
    static_audio_dir = "static/audio"
    
    pop_data, sr = generate_upbeat_pop(15)
    save_to_mp3(pop_data, sr, os.path.join(static_audio_dir, "upbeat_pop.mp3"))
    
    luxury_data, sr = generate_corporate_luxury(16)
    save_to_mp3(luxury_data, sr, os.path.join(static_audio_dir, "corporate_luxury.mp3"))
    
    elec_data, sr = generate_electronic_loop(15)
    save_to_mp3(elec_data, sr, os.path.join(static_audio_dir, "electronic_loop.mp3"))
    
    epic_data, sr = generate_dramatic_cinematic(16)
    save_to_mp3(epic_data, sr, os.path.join(static_audio_dir, "dramatic_cinematic.mp3"))
    
    print("Commercial loops generation complete!")
