# app/routes/stickynotes.py
"""
Sticky Note Operations
Handles: create, view, update, delete sticky notes on papers
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.stickynotes import StickyNote
from app.utils.papers import (
    create_success_response,
    create_error_response,
    get_user_paper_or_404,
    validate_required_fields
)

stickynotes_bp = Blueprint('stickynotes', __name__, url_prefix='/api/papers')


@stickynotes_bp.route('/<int:paper_id>/sticky-notes', methods=['POST'])
@jwt_required()
def create_sticky_note(paper_id):
    """Create a new sticky note on a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    validation_error = validate_required_fields(
        data or {}, 
        ['position_x', 'position_y', 'width', 'height', 'content']
    )
    if validation_error:
        return validation_error
    
    new_note = StickyNote(
        paper_id=paper_id,
        position_x=data['position_x'],
        position_y=data['position_y'],
        width=data['width'],
        height=data['height'],
        content=data['content'],
        user_id=get_jwt_identity()
    )
    
    db.session.add(new_note)
    db.session.commit()
    
    return create_success_response(
        'Sticky note created successfully',
        {'note': new_note.to_dict()},
        201
    )


@stickynotes_bp.route('/<int:paper_id>/sticky-notes', methods=['GET'])
@jwt_required()
def get_sticky_notes(paper_id):
    """Get all sticky notes for a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    user_id = get_jwt_identity()
    notes = StickyNote.query.filter_by(paper_id=paper_id, user_id=user_id).all()
    
    return create_success_response(
        'Sticky notes retrieved successfully',
        {
            'paper_id': paper_id,
            'notes': [note.to_dict() for note in notes]
        }
    )


@stickynotes_bp.route('/sticky-notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_sticky_note(note_id):
    """Update a sticky note"""
    user_id = get_jwt_identity()
    note = StickyNote.query.filter_by(id=note_id, user_id=user_id).first()
    
    if not note:
        return create_error_response('Sticky note not found', 404)
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['position_x', 'position_y', 'width', 'height', 'content']
    for field in allowed_fields:
        if field in data:
            setattr(note, field, data[field])
    
    db.session.commit()
    
    return create_success_response(
        'Sticky note updated successfully',
        {'note': note.to_dict()}
    )


@stickynotes_bp.route('/sticky-notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_sticky_note(note_id):
    """Delete a single sticky note"""
    user_id = get_jwt_identity()
    note = StickyNote.query.filter_by(id=note_id, user_id=user_id).first()
    
    if not note:
        return create_error_response('Sticky note not found', 404)
    
    paper_id = note.paper_id
    db.session.delete(note)
    db.session.commit()
    
    return create_success_response(
        'Sticky note deleted successfully',
        {'note_id': note_id, 'paper_id': paper_id}
    )


@stickynotes_bp.route('/<int:paper_id>/sticky-notes/all', methods=['DELETE'])
@jwt_required()
def delete_all_sticky_notes(paper_id):
    """Delete all sticky notes for a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    user_id = get_jwt_identity()
    notes = StickyNote.query.filter_by(paper_id=paper_id, user_id=user_id).all()
    
    if not notes:
        return create_error_response('No sticky notes found for this paper', 404)
    
    count = len(notes)
    for note in notes:
        db.session.delete(note)
    
    db.session.commit()
    
    return create_success_response(
        f'{count} sticky note(s) deleted successfully',
        {'paper_id': paper_id, 'deleted_count': count}
    )