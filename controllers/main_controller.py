import os
import uuid
from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from models.tts_engine import TTSEngine
from models.audio_mixer import AudioMixer

main_bp = Blueprint('main', __name__)

# Initialize the engine lazily to avoid loading heavy models during app boot
tts_engine = None

def get_tts_engine():
    global tts_engine
    if tts_engine is None:
        tts_engine = TTSEngine()
    return tts_engine

@main_bp.route('/')
def index():
    return render_template('dashboard.html')

@main_bp.route('/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    language = data.get('language', '')
    engine = data.get('engine', '')
    bg_vibe = data.get('background_vibe', 'None')
    voice = data.get('voice', 'af_heart')  # Standard default voice preset for Kokoro
    
    if not text:
        return jsonify({'error': 'Please enter some text or a slogan.'}), 400
        
    if not language or not engine:
        return jsonify({'error': 'Language and Engine selection are required.'}), 400

    # Ensure output folder exists in static directory
    output_dir = os.path.join(current_app.static_folder, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename for the output audio
    output_filename = f"generated_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        engine_obj = get_tts_engine()
        
        # Route 1: IF Language = English AND Engine = "Bark (Expressive, Slow)"
        if language == 'English' and 'Bark' in engine:
            engine_obj.generate_bark(text, output_path)
            
        # Route 2: IF Language = English AND Engine = "Kokoro (Ultra-Fast Voice + Background Music)"
        elif language == 'English' and 'Kokoro' in engine:
            # Temporary path for voice generation before mixing
            voice_temp_path = os.path.join(output_dir, f"voice_temp_{uuid.uuid4().hex}.mp3")
            try:
                engine_obj.generate_kokoro(text, voice_temp_path, voice=voice)
                
                # Check background vibe layering
                if bg_vibe and bg_vibe != 'None':
                    bg_file = 'upbeat.mp3' if bg_vibe.lower() == 'upbeat' else 'chill.mp3'
                    bg_music_path = os.path.join(current_app.static_folder, 'audio', bg_file)
                    
                    if not os.path.exists(bg_music_path):
                        return jsonify({'error': f"Background music file not found in /static/audio/: {bg_file}"}), 500
                        
                    # Layer Kokoro voice over the selected loop
                    AudioMixer.mix_voice_with_bg(voice_temp_path, bg_music_path, output_path)
                else:
                    # No background music, rename temporary voice to final output
                    os.rename(voice_temp_path, output_path)
            finally:
                # Clean up temporary voice file
                if os.path.exists(voice_temp_path):
                    try:
                        os.remove(voice_temp_path)
                    except Exception:
                        pass
                        
        # Route 3: IF Language = Bangla AND Engine = "Meta MMS / Indic-TTS (Native Bangla Speed)"
        elif language == 'Bangla' and 'Meta MMS' in engine:
            engine_obj.generate_mms_bangla(text, output_path)
            
        else:
            return jsonify({'error': f"Invalid routing combination: Language={language}, Engine={engine}"}), 400
            
        # Return URL to preview and download
        audio_url = url_for('static', filename=f"output/{output_filename}")
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'filename': output_filename
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
