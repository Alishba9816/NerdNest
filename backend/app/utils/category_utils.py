from app.models.category import Category
import re

def normalize_parent_id(parent_id):
    """Normalize parent_id: convert 0 to None, validate type"""
    if parent_id == 0 or parent_id == "0":
        return None
    if parent_id is not None:
        try:
            return int(parent_id)
        except (ValueError, TypeError):
            return None
    return parent_id

def validate_color_format(color):
    """Validate hex color format"""
    if not color:
        return True
    # Accept #RRGGBB format
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

def validate_icon_format(icon):
    """Validate icon format (assuming FontAwesome classes)"""
    if not icon:
        return True
    # Basic validation for FontAwesome classes
    return bool(re.match(r'^fa-[a-zA-Z0-9-]+$', icon))

def collect_descendant_ids(category):
    """Recursively collect all descendant category IDs."""
    descendant_ids = []
    children = Category.query.filter_by(parent_id=category.id).all()
    for child in children:
        descendant_ids.append(child.id)
        descendant_ids.extend(collect_descendant_ids(child))
    return descendant_ids

def check_name_conflict(name, user_id, exclude_id=None, parent_id=None):
    """Check if category name conflicts with existing categories for the user"""
    query = Category.query.filter_by(name=name, user_id=user_id, parent_id=parent_id)
    if exclude_id:
        query = query.filter(Category.id != exclude_id)
    return query.first() is not None

def validate_parent_exists(parent_id, user_id):
    """Validate that parent category exists and belongs to user"""
    if parent_id is None:
        return True
    parent = Category.query.filter_by(id=parent_id, user_id=user_id).first()
    return parent is not None