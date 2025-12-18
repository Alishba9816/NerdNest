# backend/app/__init__.py
from flask import Flask
from app.config import Config, FlaskConfig
from flask_cors import CORS
from app.extensions import db, bcrypt, jwt, migrate
import os

def create_app(config_object=None):
    app = Flask(__name__)

    if isinstance(config_object, dict):
        # If a dict is passed (e.g., in tests)
        app.config.update(config_object)
    elif config_object is not None:
        # If a class is passed (your normal Config)
        app.config.from_object(config_object)
    else:
        # Default fallback
        from app.config import Config
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Paper upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Register blueprints
    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)

    # Enable CORS
    from app.config import FlaskConfig
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": FlaskConfig.CORS_ORIGINS}},
         methods=FlaskConfig.CORS_METHODS,
         allow_headers=FlaskConfig.CORS_ALLOW_HEADERS, supports_credentials=True)


    return app
