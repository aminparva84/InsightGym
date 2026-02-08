"""
API endpoints for Website Knowledge Base (KB).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db, User
from services.website_kb import (
    build_kb_index,
    load_kb_index,
    get_kb_source_text,
    save_kb_source_text,
    search_kb,
)


website_kb_bp = Blueprint('website_kb', __name__, url_prefix='/api')


def _get_current_user():
    user_id_str = get_jwt_identity()
    if not user_id_str:
        return None
    try:
        return db.session.get(User, int(user_id_str))
    except (ValueError, TypeError):
        return None


def _require_admin():
    user = _get_current_user()
    if not user or user.role != 'admin':
        return None
    return user


@website_kb_bp.route('/admin/website-kb/status', methods=['GET'])
@jwt_required()
def kb_status():
    if not _require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    index = load_kb_index() or {}
    source = get_kb_source_text()
    return jsonify({
        'updated_at': index.get('updated_at'),
        'count': index.get('count', 0),
        'source_length': len(source or ''),
    }), 200


@website_kb_bp.route('/admin/website-kb/source', methods=['GET'])
@jwt_required()
def kb_source_get():
    if not _require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'content': get_kb_source_text()}), 200


@website_kb_bp.route('/admin/website-kb/source', methods=['PUT'])
@jwt_required()
def kb_source_put():
    if not _require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() or {}
    content = data.get('content')
    if content is None or not isinstance(content, str):
        return jsonify({'error': 'content is required'}), 400
    save_kb_source_text(content)
    return jsonify({'message': 'KB source saved'}), 200


@website_kb_bp.route('/admin/website-kb/reindex', methods=['POST'])
@jwt_required()
def kb_reindex():
    if not _require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        payload = build_kb_index()
        return jsonify({
            'message': 'KB reindexed',
            'count': payload.get('count', 0),
            'updated_at': payload.get('updated_at'),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
