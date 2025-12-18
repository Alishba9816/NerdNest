# backend/test_imports.py
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_extensions():
    try:
        from app.extensions import db, bcrypt, jwt
        print("✓ Extensions import successfully")
        return True
    except ImportError as e:
        print(f"✗ Extensions import error: {e}")
        return False

def test_models():
    try:
        from app.models import User, Paper, Note, Category, StickyNote
        print("✓ Models import successfully")
        return True
    except ImportError as e:
        print(f"✗ Models import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    try:
        from app import create_app
        app = create_app()
        print("✓ App created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing imports...\n")
    test_extensions()
    test_models()
    test_app_creation()