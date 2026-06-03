import os
os.environ["HF_HOME"] = r"F:\huggingface_cache"

from flask import Flask
from controllers.main_controller import main_bp

def create_app():
    # Configure custom directories for views and templates under MVC
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'text_to_audio_secret_key_12345'
    
    # Register main blueprint routes
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
