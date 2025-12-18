# app/routes/highlights.py
"""
Highlight Operations
Handles: create, view, delete highlights on papers
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.highlights_and_tags import Highlights
from app.utils.papers import (
    create_success_response,
    create_error_response,
    get_user_paper_or_404,
    validate_required_fields
)

highlights_bp = Blueprint('highlights', __name__, url_prefix='/api/papers')


@highlights_bp.route('/<int:paper_id>/highlights', methods=['POST'])
@jwt_required()
def create_highlight(paper_id):
    """Create a new highlight on a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    validation_error = validate_required_fields(
        data or {}, 
        ['start_offset', 'end_offset', 'color', 'text_content']
    )
    if validation_error:
        return validation_error
    
    new_highlight = Highlights(
        paper_id=paper_id,
        start_offset=data['start_offset'],
        end_offset=data['end_offset'],
        color=data['color'],
        text_content=data['text_content'],
        user_id=get_jwt_identity()
    )
    
    db.session.add(new_highlight)
    db.session.commit()
    
    return create_success_response(
        'Highlight created successfully',
        {'highlight': new_highlight.to_dict()},
        201
    )


@highlights_bp.route('/<int:paper_id>/highlights', methods=['GET'])
@jwt_required()
def view_highlights(paper_id):
    """Get all highlights for a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    user_id = get_jwt_identity()
    highlights = Highlights.query.filter_by(paper_id=paper_id, user_id=user_id)\
                     .order_by(Highlights.created_at.desc()).all()
    
    return create_success_response(
        'Highlights retrieved successfully',
        {
            'paper_id': paper_id,
            'highlights': [h.to_dict() for h in highlights]
        }
    )


@highlights_bp.route('/<int:paper_id>/highlights/<int:highlight_id>', methods=['DELETE'])
@jwt_required()
def remove_highlight(paper_id, highlight_id):
    """Delete a highlight from a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    user_id = get_jwt_identity()
    highlight = Highlights.query.filter_by(
        id=highlight_id, 
        paper_id=paper_id,
        user_id=user_id
    ).first()
    
    if not highlight:
        return create_error_response('Highlight not found', 404)
    
    db.session.delete(highlight)
    db.session.commit()
    
    return create_success_response(
        'Highlight deleted successfully',
        {'paper_id': paper_id, 'highlight_id': highlight_id}
    )