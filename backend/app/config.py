import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:Ph0en!x.@localhost/research_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

# Flask configuration
class FlaskConfig:
    """Flask app configuration"""
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173'] # Vite dev server
    CORS_METHODS = ['GET', 'POST', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']