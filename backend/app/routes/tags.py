# app/routes/tags.py
"""
Tag Operations
Handles: 
- Tag CRUD (create, read, update, delete tags)
- Paper-Tag associations (assign, remove tags from papers)
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.highlights_and_tags import Tags
from app.utils.papers import (
    create_success_response,
    create_error_response,
    get_user_paper_or_404,
    validate_required_fields
)

tags_bp = Blueprint('tags', __name__)


# ============= TAG CRUD OPERATIONS =============

@tags_bp.route('/api/tags', methods=['POST'])
@jwt_required()
def create_tag():
    """Create a new tag"""
    data = request.get_json()
    
    validation_error = validate_required_fields(data or {}, ['name', 'color'])
    if validation_error:
        return validation_error
    
    # Check for duplicate
    if Tags.query.filter_by(name=data['name']).first():
        return create_error_response('Tag with this name already exists', 400)
    
    new_tag = Tags(
        name=data['name'],
        color=data['color']
    )
    
    db.session.add(new_tag)
    db.session.commit()
    
    return create_success_response(
        'Tag created successfully',
        {'tag': new_tag.to_dict()},
        201
    )


@tags_bp.route('/api/tags', methods=['GET'])
@jwt_required()
def get_tags():
    """Get all tags"""
    tags = Tags.query.all()
    return create_success_response(
        'Tags retrieved successfully',
        {'tags': [tag.to_dict() for tag in tags]}
    )


@tags_bp.route('/api/tags/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """Update a tag"""
    tag = Tags.query.get(tag_id)
    if not tag:
        return create_error_response('Tag not found', 404)
    
    data = request.get_json()
    
    if 'name' in data:
        # Check for duplicate name (excluding current tag)
        existing = Tags.query.filter(
            Tags.name == data['name'],
            Tags.id != tag_id
        ).first()
        if existing:
            return create_error_response('Tag with this name already exists', 400)
        tag.name = data['name']
    
    if 'color' in data:
        tag.color = data['color']
    
    db.session.commit()
    
    return create_success_response(
        'Tag updated successfully',
        {'tag': tag.to_dict()}
    )


@tags_bp.route('/api/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Delete a tag"""
    tag = Tags.query.get(tag_id)
    if not tag:
        return create_error_response('Tag not found', 404)
    
    db.session.delete(tag)
    db.session.commit()
    
    return create_success_response(
        'Tag deleted successfully',
        {'tag_id': tag_id}
    )


# ============= PAPER-TAG ASSOCIATIONS =============

@tags_bp.route('/api/papers/<int:paper_id>/tags', methods=['GET'])
@jwt_required()
def get_paper_tags(paper_id):
    """Get all tags for a specific paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    return create_success_response(
        'Paper tags retrieved successfully',
        {
            'paper_id': paper_id,
            'tags': [tag.to_dict() for tag in paper.tags]
        }
    )


@tags_bp.route('/api/papers/<int:paper_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_paper(paper_id):
    """Add a single tag to a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    validation_error = validate_required_fields(data or {}, ['tag_id'])
    if validation_error:
        return validation_error
    
    tag = Tags.query.get(data['tag_id'])
    if not tag:
        return create_error_response('Tag not found', 404)
    
    if tag in paper.tags:
        return create_error_response('Tag already associated with this paper', 400)
    
    paper.tags.append(tag)
    db.session.commit()
    
    return create_success_response(
        'Tag added to paper successfully',
        {
            'paper_id': paper_id,
            'tag': tag.to_dict()
        },
        201
    )


@tags_bp.route('/api/papers/<int:paper_id>/tags/assign', methods=['POST'])
@jwt_required()
def assign_multiple_tags(paper_id):
    """Assign multiple tags to a paper at once"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    data = request.get_json()
    validation_error = validate_required_fields(data or {}, ['tag_ids'])
    if validation_error:
        return validation_error
    
    tag_ids = data['tag_ids']
    if not isinstance(tag_ids, list) or not all(isinstance(tid, int) for tid in tag_ids):
        return create_error_response('tag_ids must be a list of integers', 400)
    
    tags = Tags.query.filter(Tags.id.in_(tag_ids)).all()
    if not tags:
        return create_error_response('No valid tags found', 404)
    
    added_tags = []
    for tag in tags:
        if tag not in paper.tags:
            paper.tags.append(tag)
            added_tags.append(tag)
    
    db.session.commit()
    
    return create_success_response(
        f'{len(added_tags)} tag(s) assigned to paper',
        {
            'paper_id': paper_id,
            'added_tags': [tag.to_dict() for tag in added_tags]
        },
        201
    )


@tags_bp.route('/api/papers/<int:paper_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_paper(paper_id, tag_id):
    """Remove a tag from a paper"""
    paper, error = get_user_paper_or_404(paper_id)
    if error:
        return error
    
    tag = Tags.query.get(tag_id)
    if not tag:
        return create_error_response('Tag not found', 404)
    
    if tag not in paper.tags:
        return create_error_response('Tag not associated with this paper', 400)
    
    paper.tags.remove(tag)
    db.session.commit()
    
    return create_success_response(
        'Tag removed from paper successfully',
        {'paper_id': paper_id, 'tag_id': tag_id}
    )