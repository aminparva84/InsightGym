"""
API endpoints for Website Knowledge Base (KB).
Admin routes (status, source, reindex) are in admin_api.py.
This file only has the query route for authenticated users.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.website_kb import search_kb


website_kb_bp = Blueprint('website_kb', __name__, url_prefix='/api')


def _get_db():
    return current_app.extensions['sqlalchemy']


def _get_user_model():
    from app import User
    return User


def _get_current_user():
    user_id_str = get_jwt_identity()
    if not user_id_str:
        return None
    try:
        db = _get_db()
        User = _get_user_model()
        return db.session.get(User, int(user_id_str))
    except (ValueError, TypeError):
        return None


@website_kb_bp.route('/website-kb/query', methods=['POST'])
@jwt_required()
def kb_query():
    user = _get_current_user()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    data = request.get_json() or {}
    query = data.get('query') or ''
    if not query.strip():
        return jsonify({'error': 'Query is required'}), 400
    top_k = data.get('top_k', 3)
    try:
        top_k = int(top_k)
    except (ValueError, TypeError):
        top_k = 3
    results = search_kb(query, top_k=top_k)
    return jsonify({'query': query, 'results': results}), 200
