import os
from flask import Flask
from flask_cors import CORS
from processing.video_processing_service import user_service

def create_app() -> Flask:
    """Create flask app."""
    app = Flask(__name__)
  
    CORS(app)

    app.secret_key = os.environ.get("SECRET_KEY", 'your_secret_key')
    app.register_blueprint(user_service)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)