# app/routes/papers.py
"""
Paper CRUD Operations
Handles: upload, view, download, delete, read/unread status, categories
"""
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.paper import Paper
from app.models.category import Category
from app.utils.papers import (
    create_success_response, 
    create_error_response,
    get_user_paper_or_404,
    validate_required_fields,
    save_uploaded_file,
    format_paper_data,
    get_user_categories,
    associate_paper_with_category,
    format_paper_data
)

papers_bp = Blueprint('papers', __name__, url_prefix='/api/papers')


@papers_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_paper():
    """Upload a new paper with PDF file"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return create_error_response('No file provided')
    
    form_data = request.form.to_dict()
    validation_error = validate_required_fields(form_data, ['title'])
    if validation_error:
        return validation_error
    
    file_path, file_error = save_uploaded_file(request.files['file'])
    if file_error:
        return file_error
    
    paper = Paper(
        title=form_data['title'],
        authors=form_data.get('authors', ''),
        abstract=form_data.get('abstract', ''),
        file_path=file_path,
        user_id=user_id
    )
    
    db.session.add(paper)
    associate_paper_with_category(paper, form_data.get('category_id'))
    db.session.commit()
    
    return create_success_response(
        'Paper uploaded successfully',
        {'paper_id': paper.id, 'title': paper.title},
        201
    )


@papers_bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required()
def view_paper(paper_id):
    """Get a specific paper's details"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    return create_success_response(
        'Paper retrieved successfully',
        {'paper': format_paper_data(paper)}
    )


@papers_bp.route('/<int:paper_id>/download', methods=['GET'])
@jwt_required()
def download_paper(paper_id):
    """Download the PDF file"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    try:
        return send_file(paper.file_path, as_attachment=False)
    except FileNotFoundError:
        return create_error_response('File not found', 404)


@papers_bp.route('/<int:paper_id>', methods=['DELETE'])
@jwt_required()
def delete_paper(paper_id):
    """Delete a paper and all associated data"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    # CASCADE deletion should handle notes, highlights, sticky notes, tags
    db.session.delete(paper)
    db.session.commit()
    
    return create_success_response(
        'Paper deleted successfully',
        {'paper_id': paper_id}
    )


@papers_bp.route('/<int:paper_id>/toggle-read', methods=['PUT'])
@jwt_required()
def toggle_read_status(paper_id):
    """Toggle paper read/unread status"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    paper.is_read = not paper.is_read
    db.session.commit()
    
    status = "read" if paper.is_read else "unread"
    return create_success_response(
        f'Paper marked as {status}',
        {'paper_id': paper_id, 'is_read': paper.is_read}
    )


@papers_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all categories for current user"""
    categories = get_user_categories()
    return create_success_response(
        'Categories retrieved successfully',
        {'categories': categories}
    )


@papers_bp.route('', methods=['GET'])
@jwt_required()
def get_all_papers():
    """Get all papers for the current user"""
    user_id = get_jwt_identity()
    
    # Get all papers ordered by upload date (newest first)
    papers = Paper.query.filter_by(user_id=user_id)\
                        .order_by(Paper.upload_date.desc()).all()
    
    return create_success_response(
        'Papers retrieved successfully',
        {'papers': [format_paper_data(p) for p in papers]}
    )

@papers_bp.route('/<int:paper_id>/categories', methods=['GET'])
@jwt_required()
def get_paper_categories(paper_id):
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    categories = [cat.to_dict() for cat in paper.categories]
    
    return create_success_response(
        'Categories retrieved successfully',
        {
            'paper_id': paper_id,
            'categories': categories,
            'count': len(categories)
        }
    )


@papers_bp.route('/<int:paper_id>/categories', methods=['POST'])
@jwt_required()
def assign_paper_to_category(paper_id):
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    if not data or 'category_id' not in data:
        return create_error_response('category_id is required', 400)
    
    category_id = data['category_id']
    user_id = get_jwt_identity()
    
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return create_error_response('Category not found', 404)
    
    if category in paper.categories:
        return create_error_response('Already assigned', 400)
    
    paper.categories.append(category)
    db.session.commit()
    
    return create_success_response('Assigned successfully', {}, 201)