"""
API endpoint for AI action planning and execution.
Prefer POST /api/chat for unified flow (Real_State style); this endpoint is kept for backward compatibility.
"""

import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db, User, ChatHistory, ChatSession
from services.action_planner import plan_and_execute
from services.ai_debug_logger import append_log


ai_plan_bp = Blueprint('ai_plan', __name__, url_prefix='/api/ai')


@ai_plan_bp.route('/plan', methods=['POST'])
@jwt_required()
def plan_actions_endpoint():
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        message = data.get('message')
        if not message or not isinstance(message, str):
            return jsonify({'error': 'Message is required'}), 400

        session_id = (data.get('session_id') or '').strip() or None
        if not session_id:
            session_id = str(uuid.uuid4())

        language = user.language if getattr(user, 'language', None) else 'fa'
        result = plan_and_execute(message, user, language)

        # Save in chat history for continuity
        chat_entry = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=result.get('assistant_response') or ''
        )
        db.session.add(chat_entry)
        existing = ChatSession.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not existing:
            db.session.add(ChatSession(session_id=session_id, user_id=user_id, title=None))
        db.session.commit()

        try:
            append_log(
                message=message,
                response=result.get('assistant_response') or '',
                action_json={
                    'actions': result.get('actions', []),
                    'results': result.get('results', []),
                    'errors': result.get('errors', []),
                },
                error='',
            )
        except Exception:
            pass

        return jsonify({
            'assistant_response': result.get('assistant_response'),
            'actions': result.get('actions', []),
            'results': result.get('results', []),
            'errors': result.get('errors', []),
            'session_id': session_id,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
