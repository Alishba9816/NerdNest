# app/routes/notes.py
"""
Paper Notes Operations
Handles: create, view, delete notes associated with papers
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.note import Note
from app.utils.papers import (
    create_success_response,
    create_error_response,
    get_user_paper_or_404,
    get_user_note_or_404,
    validate_required_fields,
    format_note_data
)

notes_bp = Blueprint('notes', __name__, url_prefix='/api/papers')


@notes_bp.route('/<int:paper_id>/notes', methods=['GET'])
@jwt_required()
def get_notes(paper_id):
    """Get all notes for a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(paper_id=paper_id, user_id=user_id)\
                     .order_by(Note.created_at.desc()).all()
    
    return create_success_response(
        'Notes retrieved successfully',
        {'notes': [format_note_data(note) for note in notes]}
    )


@notes_bp.route('/<int:paper_id>/notes', methods=['POST'])
@jwt_required()
def add_note(paper_id):
    """Add a new note to a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    validation_error = validate_required_fields(data or {}, ['content'])
    if validation_error:
        return validation_error
    
    note = Note(
        content=data['content'].strip(),
        paper_id=paper_id,
        user_id=get_jwt_identity()
    )
    db.session.add(note)
    db.session.commit()
    
    return create_success_response(
        'Note added successfully',
        {'note': format_note_data(note)},
        201
    )


@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a specific note"""
    note, error = get_user_note_or_404(note_id)
    if error:
        return error
    
    paper_id = note.paper_id
    db.session.delete(note)
    db.session.commit()
    
    return create_success_response(
        'Note deleted successfully',
        {'note_id': note_id, 'paper_id': paper_id}
    )