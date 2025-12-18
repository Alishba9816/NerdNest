from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.paper import Paper
from app.models.category import Category
from rapidfuzz import fuzz   # <-- FIX HERE

main_bp = Blueprint('main', __name__, url_prefix="/api")


@main_bp.route('/dashboard')
@jwt_required()
def api_dashboard():
    user_id = get_jwt_identity()
    
    recent_papers = Paper.query.filter_by(user_id=user_id)\
        .order_by(Paper.upload_date.desc()).limit(5).all()
    user_categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify({
        "recent_papers": [p.to_dict() for p in recent_papers],
        "user_categories": [c.to_dict() for c in user_categories]
    }), 200


@main_bp.route('/search-all', methods=['GET'])
@jwt_required()
def search_all():
    user_id = get_jwt_identity()
    query = request.args.get('q', '').strip().lower()

    if not query:
        return jsonify({"error": "Search query is required."}), 400

    results = []

    papers = Paper.query.filter_by(user_id=user_id).all()
    categories = Category.query.filter_by(user_id=user_id).all()

    # Search in papers
    for paper in papers:
        title = (paper.title or "").lower()
        authors = (paper.authors or "").lower()

        if fuzz.partial_ratio(query, title) >= 70 or fuzz.partial_ratio(query, authors) >= 70:
            results.append({
                "type": "paper",
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors
            })

    # Search in categories
    for category in categories:
        name = (category.name or "").lower()
        if fuzz.partial_ratio(query, name) >= 70:
            results.append({
                "type": "category",
                "id": category.id,
                "name": category.name
            })

    if not results:
        return jsonify({"message": "No results found."}), 404

    return jsonify({"results": results}), 200
