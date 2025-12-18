# backend/app/extensions.py
"""
Flask extensions initialized here to avoid circular imports.
Extensions are created here but initialized in create_app()
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Create extension instances
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()