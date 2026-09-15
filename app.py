import os
from flask import Flask
from config import Config
from models import db
from routes.resume_routes import resume_bp
from routes.ai_routes import ai_bp
from routes.export_routes import export_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(resume_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(export_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("=" * 60)
    print("AI Resume Builder is running at http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
