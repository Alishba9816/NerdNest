# tests/conftest.py
"""
Configuration file for pytest
Contains fixtures (reusable test data) used across all test files
"""
import pytest
import os
import tempfile
from app import create_app, db, bcrypt
from app.models.user import User
from app.models.paper import Paper
from app.models.category import Category
from app.models.note import Note
from app.models.highlights_and_tags import Highlights, Tags
from app.models.stickynotes import StickyNote
from flask_jwt_extended import create_access_token


# ============= APP & DATABASE FIXTURES =============

@pytest.fixture(scope='function')
def app():
    """Create a Flask app for testing with in-memory SQLite"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })

    # Create database tables
    with app.app_context():
        db.create_all()

    yield app  # Tests run here

    # Teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()



@pytest.fixture(scope='function')
def client(app):
    """
    Create a test client to make requests
    This is like a fake browser
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create a CLI runner for testing CLI commands
    """
    return app.test_cli_runner()


# ============= USER FIXTURES =============

@pytest.fixture(scope='function')
def test_user(app):
    """
    Create a test user in the database
    Password is 'password123'
    """
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(
            username='testuser',
            email='test@example.com',
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(user)
        user_id = user.id
        
    return {
        'id': user_id,
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'  # Plain text for testing login
    }


@pytest.fixture(scope='function')
def second_user(app):
    """
    Create a second user for testing authorization
    Used to test that users can't access each other's data
    """
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password456').decode('utf-8')
        user = User(
            username='otheruser',
            email='other@example.com',
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        db.session.refresh(user)
        user_id = user.id
        
    return {
        'id': user_id,
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'password456'
    }


# ============= AUTHENTICATION FIXTURES =============

@pytest.fixture(scope='function')
def auth_token(app, test_user):
    """
    Generate JWT access token for test_user
    Use this to make authenticated requests
    
    Usage:
        response = client.get('/api/papers/1',
                             headers={'Authorization': f'Bearer {auth_token}'})
    """
    with app.app_context():
        token = create_access_token(identity=str(test_user['id']))
    return token


@pytest.fixture(scope='function')
def second_auth_token(app, second_user):
    """
    Generate JWT token for second_user
    Used to test authorization (user A can't access user B's data)
    """
    with app.app_context():
        token = create_access_token(identity=str(second_user['id']))
    return token


@pytest.fixture(scope='function')
def auth_headers(auth_token):
    """
    Return properly formatted authorization headers
    Convenience fixture to avoid repeating header format
    
    Usage:
        response = client.get('/api/papers/1', headers=auth_headers)
    """
    return {'Authorization': f'Bearer {auth_token}'}


# ============= DATA FIXTURES =============

@pytest.fixture(scope='function')
def test_category(app, test_user):
    """
    Create a test category for organizing papers
    """
    with app.app_context():
        category = Category(
            name='Machine Learning',
            user_id=test_user['id']
        )
        db.session.add(category)
        db.session.commit()
        
        db.session.refresh(category)
        category_data = {
            'id': category.id,
            'name': category.name,
            'user_id': category.user_id
        }
    
    return category_data


@pytest.fixture(scope='function')
def test_paper(app, test_user):
    """
    Create a test paper (without actual file)
    Returns paper data as dictionary
    """
    with app.app_context():
        paper = Paper(
            title='Test Research Paper',
            authors='John Doe, Jane Smith',
            abstract='This is a test abstract about machine learning.',
            file_path='/fake/path/test.pdf',  # Fake path for testing
            user_id=test_user['id'],
            is_read=False
        )
        db.session.add(paper)
        db.session.commit()
        
        db.session.refresh(paper)
        paper_data = {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'file_path': paper.file_path,
            'user_id': paper.user_id,
            'is_read': paper.is_read
        }
    
    return paper_data


@pytest.fixture(scope='function')
def test_note(app, test_paper, test_user):
    """
    Create a test note on test_paper
    """
    with app.app_context():
        note = Note(
            content='This is a test note about the paper.',
            paper_id=test_paper['id'],
            user_id=test_user['id']
        )
        db.session.add(note)
        db.session.commit()
        
        db.session.refresh(note)
        note_data = {
            'id': note.id,
            'content': note.content,
            'paper_id': note.paper_id,
            'user_id': note.user_id
        }
    
    return note_data


@pytest.fixture(scope='function')
def test_highlight(app, test_paper, test_user):
    """
    Create a test highlight on test_paper
    """
    with app.app_context():
        highlight = Highlights(
            paper_id=test_paper['id'],
            start_offset=100,
            end_offset=200,
            color='#FFFF00',  # Yellow
            text_content='This is the highlighted text',
            user_id=test_user['id']
        )
        db.session.add(highlight)
        db.session.commit()
        
        db.session.refresh(highlight)
        highlight_data = {
            'id': highlight.id,
            'paper_id': highlight.paper_id,
            'start_offset': highlight.start_offset,
            'end_offset': highlight.end_offset,
            'color': highlight.color,
            'text_content': highlight.text_content,
            'user_id': highlight.user_id
        }
    
    return highlight_data


@pytest.fixture(scope='function')
def test_tag(app):
    """
    Create a test tag (tags are global, not user-specific)
    """
    with app.app_context():
        tag = Tags(
            name='Machine Learning',
            color='#FF5733'
        )
        db.session.add(tag)
        db.session.commit()
        
        db.session.refresh(tag)
        tag_data = {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color
        }
    
    return tag_data


@pytest.fixture(scope='function')
def test_sticky_note(app, test_paper, test_user):
    """
    Create a test sticky note on test_paper
    """
    with app.app_context():
        sticky = StickyNote(
            paper_id=test_paper['id'],
            position_x=100,
            position_y=200,
            width=150,
            height=100,
            content='Remember to review this section!',
            user_id=test_user['id']
        )
        db.session.add(sticky)
        db.session.commit()
        
        db.session.refresh(sticky)
        sticky_data = {
            'id': sticky.id,
            'paper_id': sticky.paper_id,
            'position_x': sticky.position_x,
            'position_y': sticky.position_y,
            'width': sticky.width,
            'height': sticky.height,
            'content': sticky.content,
            'user_id': sticky.user_id
        }
    
    return sticky_data


# ============= FILE UPLOAD FIXTURES =============

@pytest.fixture(scope='function')
def mock_pdf_file():
    """
    Create a mock PDF file for upload testing
    Returns a file-like object that can be used in form data
    """
    from io import BytesIO
    
    # Create fake PDF content
    pdf_content = b'%PDF-1.4 fake pdf content for testing'
    
    return (BytesIO(pdf_content), 'test_paper.pdf')


# ============= HELPER FIXTURES =============

@pytest.fixture(scope='function')
def sample_paper_data():
    """
    Return sample paper data for creation tests
    """
    return {
        'title': 'Neural Networks Explained',
        'authors': 'Dr. Smith, Dr. Jones',
        'abstract': 'A comprehensive guide to neural networks and deep learning.'
    }


@pytest.fixture(scope='function')
def sample_highlight_data():
    """
    Return sample highlight data for creation tests
    """
    return {
        'start_offset': 150,
        'end_offset': 350,
        'color': '#00FF00',  # Green
        'text_content': 'Important finding: accuracy improved by 25%'
    }


@pytest.fixture(scope='function')
def sample_sticky_note_data():
    """
    Return sample sticky note data for creation tests
    """
    return {
        'position_x': 250,
        'position_y': 400,
        'width': 200,
        'height': 150,
        'content': 'Follow up on this research'
    }