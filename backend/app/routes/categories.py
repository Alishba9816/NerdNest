# categories.py file
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.category import Category
from app.models.paper import Paper
from app.models.base import paper_categories
import re
import logging
from app.utils.category_utils import (
    normalize_parent_id,
    validate_color_format,
    validate_icon_format,
    validate_parent_exists,
    collect_descendant_ids,
    check_name_conflict
)

# — Unique blueprint name + URL prefix to avoid collisions across the app
categories_bp = Blueprint('categories_bp', __name__, url_prefix='/api/categories')

# Configure logging
logger = logging.getLogger(__name__)


# View all categories
@categories_bp.route('/view_all', methods=['GET'])
@jwt_required()
def view_all_categories():
    """Display all top-level categories (categories without parents)."""
    try:
        user_id = get_jwt_identity()
        categories = Category.query.filter_by(user_id=user_id, parent_id=None).order_by(Category.name).all()
        logger.info(f"Retrieved {len(categories)} top-level categories for user {user_id}")
        return jsonify({
            "categories": [cat.to_dict() for cat in categories],
            "total": len(categories)
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving categories for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve categories"}), 500


# View a specific category and its papers
@categories_bp.route('/view/<int:category_id>', methods=['GET'])
@jwt_required()
def view_category(category_id):
    """Return a specific category and its papers in JSON."""
    try:
        user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
        logger.info(f"Retrieved category {category_id} for user {user_id}")
        return jsonify({
            "category": category.to_dict(),
            "papers": [paper.to_dict() for paper in category.papers],
            "paper_count": len(category.papers)
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving category {category_id} for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve category"}), 500


# Create a new category
@categories_bp.route('/create', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category with comprehensive validation."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Category name is required."}), 400

        name = data.get('name').strip()
        if not name:
            return jsonify({"error": "Category name cannot be empty."}), 400
        if len(name) > 100:
            return jsonify({"error": "Category name cannot exceed 100 characters."}), 400

        color = data.get('color', "#3498db")
        icon = data.get('icon', "fa-folder")
        parent_id = normalize_parent_id(data.get('parent_id'))

        if not validate_color_format(color):
            return jsonify({"error": "Invalid color format. Use #RRGGBB format."}), 400
        if not validate_icon_format(icon):
            return jsonify({"error": "Invalid icon format. Use FontAwesome class format (fa-*)."}), 400
        if not validate_parent_exists(parent_id, user_id):
            return jsonify({"error": "Parent category not found."}), 404

        if check_name_conflict(name, user_id, parent_id=parent_id):
            parent_name = "root" if parent_id is None else Category.query.get(parent_id).name
            return jsonify({"error": f"Category '{name}' already exists in {parent_name}."}), 400

        new_category = Category(
            name=name,
            color=color,
            icon=icon,
            parent_id=parent_id,
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()

        logger.info(f"Created category '{name}' (ID: {new_category.id}) for user {user_id}")
        return jsonify({
            "message": "Category created successfully.",
            "category": new_category.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to create category"}), 500


# Get available parent categories for a category being edited
@categories_bp.route('/<int:category_id>/available_parents', methods=['GET'])
@jwt_required()
def get_available_parents(category_id):
    """Return valid parent categories for a category being edited (avoid circular reference)."""
    try:
        user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

        descendant_ids = collect_descendant_ids(category)
        descendant_ids.append(category.id)

        valid_parents = Category.query.filter(
            Category.user_id == user_id,
            ~Category.id.in_(descendant_ids)
        ).order_by(Category.name).all()

        logger.info(f"Retrieved {len(valid_parents)} valid parent options for category {category_id}")
        return jsonify([
            {"id": cat.id, "name": cat.name, "level": cat.get_level()}
            for cat in valid_parents
        ]), 200

    except Exception as e:
        logger.error(f"Error getting available parents for category {category_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve available parents"}), 500


# List child categories for a given parent category
@categories_bp.route('/<int:category_id>/children', methods=['GET'])
@jwt_required()
def list_child_categories(category_id):
    """Return child categories for a given parent category (belonging to the logged-in user)."""
    try:
        user_id = get_jwt_identity()
        parent_category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
        children = Category.query.filter_by(parent_id=category_id, user_id=user_id).order_by(Category.name).all()

        logger.info(f"Retrieved {len(children)} child categories for category {category_id}")
        return jsonify({
            "parent_id": category_id,
            "parent_name": parent_category.name,
            "children": [child.to_dict() for child in children],
            "total": len(children)
        }), 200

    except Exception as e:
        logger.error(f"Error getting child categories for category {category_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve child categories"}), 500


# Update a category with comprehensive validation
@categories_bp.route('/<int:category_id>/update', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """API endpoint to update a category, with comprehensive validation."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

        if "name" in data:
            new_name = data["name"].strip()
            if not new_name:
                return jsonify({"error": "Category name cannot be empty."}), 400
            if len(new_name) > 100:
                return jsonify({"error": "Category name cannot exceed 100 characters."}), 400
            if new_name != category.name and check_name_conflict(new_name, user_id, exclude_id=category_id, parent_id=category.parent_id):
                return jsonify({"error": "Category with this name already exists in the same location."}), 400

        if "color" in data and not validate_color_format(data["color"]):
            return jsonify({"error": "Invalid color format. Use #RRGGBB format."}), 400
        if "icon" in data and not validate_icon_format(data["icon"]):
            return jsonify({"error": "Invalid icon format. Use FontAwesome class format (fa-*)."}), 400

        new_parent_id = normalize_parent_id(data.get("parent_id", category.parent_id))
        if new_parent_id != category.parent_id:
            if not validate_parent_exists(new_parent_id, user_id):
                return jsonify({"error": "Parent category not found."}), 404

            descendant_ids = collect_descendant_ids(category)
            descendant_ids.append(category_id)
            if new_parent_id and new_parent_id in descendant_ids:
                return jsonify({"error": "Cannot assign a category as a child of itself or its descendant."}), 400

            if "name" in data:
                new_name = data["name"].strip()
            else:
                new_name = category.name

            if check_name_conflict(new_name, user_id, exclude_id=category_id, parent_id=new_parent_id):
                parent_name = "root" if new_parent_id is None else Category.query.get(new_parent_id).name
                return jsonify({"error": f"Category '{new_name}' already exists in {parent_name}."}), 400

        if "name" in data:
            category.name = data["name"].strip()
        if "color" in data:
            category.color = data["color"]
        if "icon" in data:
            category.icon = data["icon"]

        category.parent_id = new_parent_id
        db.session.commit()

        logger.info(f"Updated category {category_id} for user {user_id}")
        return jsonify({
            "message": "Category updated successfully.",
            "category": category.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating category {category_id} for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to update category"}), 500


# Delete a category with proper child reassignment and name conflict resolution
@categories_bp.route('/<int:category_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category with proper child reassignment and name conflict resolution."""
    try:
        user_id = get_jwt_identity()
        with db.session.begin():
            category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
            children = category.children  # adjust .all() if children is dynamic

            logger.info(f"Processing {len(children)} child categories for deletion of category {category_id}")
            for child in children:
                existing = Category.query.filter_by(
                    name=child.name, parent_id=None, user_id=user_id
                ).first()

                if existing:
                    base_name = child.name
                    suffix = 1
                    new_name = f"{base_name} (moved)"
                    while Category.query.filter_by(name=new_name, parent_id=None, user_id=user_id).first():
                        suffix += 1
                        new_name = f"{base_name} (moved {suffix})"
                    logger.info(f"Renaming child category '{child.name}' to '{new_name}' to avoid conflict")
                    child.name = new_name

                child.parent_id = None

            paper_count = len(category.papers)
            category.papers.clear()
            category_name = category.name
            db.session.delete(category)

            logger.info(f"Deleted category '{category_name}' (ID: {category_id}), reassigned {len(children)} children, detached {paper_count} papers")

        return jsonify({
            "message": "Category deleted successfully.",
            "details": {
                "category_name": category_name,
                "children_reassigned": len(children),
                "papers_detached": paper_count
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category {category_id} for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to delete category"}), 500
