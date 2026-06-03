import os
import uuid
import shutil
from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from models.tts_engine import TTSEngine
from models.audio_mixer import AudioMixer

main_bp = Blueprint('main', __name__)

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
    # Handle both multipart/form-data (for voice cloning upload) and JSON requests
    if request.content_type and 'multipart/form-data' in request.content_type:
        text = request.form.get('text', '').strip()
        language = request.form.get('language', 'english').lower()
        engine = request.form.get('engine', '').strip()
        vibe = request.form.get('vibe', 'corporate').lower()
        intensity = int(request.form.get('intensity', '70'))
        speed = float(request.form.get('speed', '1.0'))
        
        layer_bg = request.form.get('layer_bg') == 'true'
        bg_style = request.form.get('bg_style', 'corporate_luxury').strip()
        voice_vol = int(request.form.get('voice_vol', '100'))
        bg_vol = int(request.form.get('bg_vol', '40'))
        ducking = int(request.form.get('ducking', '15'))
        
        # Target voice reference file
        voice_ref_file = request.files.get('voice_ref')
    else:
        # Fallback to JSON
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        language = data.get('language', 'english').lower()
        engine = data.get('engine', '').strip()
        vibe = data.get('vibe', 'corporate').lower()
        intensity = int(data.get('intensity', '70'))
        speed = float(data.get('speed', '1.0'))
        
        layer_bg = data.get('layer_bg', False)
        bg_style = data.get('bg_style', 'corporate_luxury').strip()
        voice_vol = int(data.get('voice_vol', '100'))
        bg_vol = int(data.get('bg_vol', '40'))
        ducking = int(data.get('ducking', '15'))
        voice_ref_file = None

    if not text:
        return jsonify({'error': 'Please enter some campaign script text.'}), 400
        
    if not engine:
        return jsonify({'error': 'Engine selection is required.'}), 400

    # Ensure output folders exist
    output_dir = os.path.join(current_app.static_folder, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save voice cloning reference if uploaded
    voice_ref_path = None
    if voice_ref_file and voice_ref_file.filename != '':
        uploads_dir = os.path.join(output_dir, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        safe_filename = f"ref_{uuid.uuid4().hex}_{secure_filename_fallback(voice_ref_file.filename)}"
        voice_ref_path = os.path.join(uploads_dir, safe_filename)
        voice_ref_file.save(voice_ref_path)

    # Generate temporary voice file
    voice_temp_filename = f"voice_temp_{uuid.uuid4().hex}.mp3"
    voice_temp_path = os.path.join(output_dir, voice_temp_filename)
    
    # Generate final mixed path
    output_filename = f"generated_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        engine_obj = get_tts_engine()
        
        # Generate raw speech
        engine_obj.generate_ad_campaign(
            text=text,
            output_path=voice_temp_path,
            model_name=engine,
            language=language,
            vibe=vibe,
            emotional_intensity=intensity,
            pacing_speed=speed,
            voice_ref_path=voice_ref_path
        )
        
        # Run background music mixing if requested
        if layer_bg:
            bg_music_path = os.path.join(current_app.static_folder, 'audio', f"{bg_style}.mp3")
            if not os.path.exists(bg_music_path):
                return jsonify({'error': f"Background loop '{bg_style}.mp3' was not found on system."}), 500
                
            AudioMixer.mix_voice_with_bg(
                voice_path=voice_temp_path,
                bg_music_path=bg_music_path,
                output_path=output_path,
                voice_vol_pct=voice_vol,
                bg_vol_pct=bg_vol,
                ducking_threshold=ducking
            )
        else:
            # Move voice file directly to output path
            shutil.move(voice_temp_path, output_path)
            
        # Clean up temporary raw voice file if still exists
        if os.path.exists(voice_temp_path):
            try:
                os.remove(voice_temp_path)
            except Exception:
                pass
                
        # Clean up uploaded reference file to prevent disk fill
        if voice_ref_path and os.path.exists(voice_ref_path):
            try:
                os.remove(voice_ref_path)
            except Exception:
                pass

        audio_url = url_for('static', filename=f"output/{output_filename}")
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'filename': output_filename
        })
        
    except Exception as e:
        # Cleanup on failure
        for p in [voice_temp_path, voice_ref_path]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Generation failed: {str(e)}"}), 500

def secure_filename_fallback(filename):
    """Simple sanitization fallback for uploaded filenames."""
    import re
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
