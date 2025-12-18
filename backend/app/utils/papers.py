from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app.models.paper import Paper
from app.models.note import Note
from app.models.category import Category


def create_success_response(message, data=None, status_code=200):
    """Create a standardized success response"""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code


def create_error_response(message, status_code=400):
    """Create a standardized error response"""
    return jsonify({'error': message}), status_code


def get_user_paper_or_404(paper_id):
    """Get a paper that belongs to the current user or return 404 error"""
    user_id = get_jwt_identity()
    paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
    
    if not paper:
        return None, create_error_response('Paper not found', 404)
    
    return paper, None


def get_user_note_or_404(note_id):
    """Get a note that belongs to the current user or return 404 error"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    
    if not note:
        return None, create_error_response('Note not found', 404)
    
    return note, None


def validate_required_fields(data, required_fields):
    """Validate that required fields are present and not empty"""
    errors = []
    for field in required_fields:
        if field not in data or not data[field] or not str(data[field]).strip():
            errors.append(f'{field.replace("_", " ").title()} is required')
    
    if errors:
        return create_error_response('; '.join(errors), 400)
    
    return None


def save_uploaded_file(file):
    """Save uploaded file and return file path"""
    if not file or file.filename == '':
        return None, create_error_response('No file provided', 400)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
        return file_path, None
    except Exception as e:
        return None, create_error_response(f'Failed to save file: {str(e)}', 500)


def format_paper_data(paper):
    """Format paper data for API response"""
    return {
        'id': paper.id,
        'title': paper.title,
        'authors': paper.authors,
        'abstract': paper.abstract,
        'is_read': paper.is_read,
        'created_at': paper.created_at.isoformat() if paper.created_at else None,
        'categories': [{'id': cat.id, 'name': cat.name} for cat in paper.categories]
    }


def format_note_data(note):
    """Format note data for API response"""
    return {
        'id': note.id,
        'content': note.content,
        'created_at': note.created_at.isoformat() if note.created_at else None
    }


def format_category_data(category):
    """Format category data for API response"""
    return {
        'id': category.id,
        'name': category.name
    }


def get_user_categories():
    """Get all categories for the current user"""
    user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=user_id).all()
    return [format_category_data(cat) for cat in categories]


def associate_paper_with_category(paper, category_id):
    """Associate a paper with a category if valid"""
    if not category_id or category_id == '0':
        return True
    
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if category:
        paper.categories.append(category)
        return True
    
    return False

def format_paper_data(paper):
    """Format paper data for API response"""
    return {
        'id': paper.id,
        'title': paper.title,
        'authors': paper.authors,
        'abstract': paper.abstract,
        'file_path': paper.file_path,
        'upload_date': paper.upload_date.isoformat() if paper.upload_date else None,
        'is_read': paper.is_read,
        'user_id': paper.user_id
    }