"""
Member-to-trainer messaging API.
Members can send messages to their assigned trainer (admin or assistant).
Trainers (admin/assistant) can see messages from their assigned members and reply.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


def _get_db():
    """Get database instance from current app context."""
    return current_app.extensions['sqlalchemy']


def _get_user_model():
    from app import User
    return User


def _get_trainer_message_model():
    from app import TrainerMessage
    return TrainerMessage


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


@messages_bp.route('', methods=['GET'])
@jwt_required()
def list_threads():
    """
    List conversations.
    - Member: returns their assigned trainer (single thread).
    - Admin/Assistant: returns list of members they have messages with (thread list with last message and unread count).
    """
    db = _get_db()
    User = _get_user_model()
    TrainerMessage = _get_trainer_message_model()

    current = _get_current_user()
    if not current:
        return jsonify({'error': 'Invalid token'}), 401

    with_user_id = request.args.get('with', type=int)

    if current.role == 'member':
        # Member: can only have one thread (with assigned_to)
        trainer_id = getattr(current, 'assigned_to', None)
        if not trainer_id:
            return jsonify({
                'threads': [],
                'trainer': None,
                'message': 'No trainer assigned'
            }), 200
        trainer = db.session.get(User, trainer_id)
        if not trainer:
            return jsonify({'threads': [], 'trainer': None}), 200
        # Return trainer info for the single thread
        return jsonify({
            'threads': [{
                'user_id': trainer.id,
                'username': trainer.username,
                'unread_count': db.session.query(TrainerMessage).filter(
                    TrainerMessage.sender_id == trainer_id,
                    TrainerMessage.recipient_id == current.id,
                    TrainerMessage.read_at.is_(None)
                ).count()
            }],
            'trainer': {
                'id': trainer.id,
                'username': trainer.username
            }
        }), 200

    # Admin or assistant: list members they have conversations with
    if current.role not in ('admin', 'assistant'):
        return jsonify({'error': 'Forbidden'}), 403

    # Get assigned member IDs (admin: all members; assistant: only assigned)
    if current.role == 'admin':
        members = db.session.query(User).filter_by(role='member').all()
    else:
        members = db.session.query(User).filter_by(role='member', assigned_to=current.id).all()
    member_ids = [u.id for u in members]

    if not member_ids:
        return jsonify({'threads': []}), 200

    # If ?with=USER_ID, we still return thread list but frontend will open that thread
    threads = []
    for mid in member_ids:
        member = db.session.get(User, mid)
        if not member:
            continue
        last_msg = db.session.query(TrainerMessage).filter(
            ((TrainerMessage.sender_id == current.id) & (TrainerMessage.recipient_id == mid)) |
            ((TrainerMessage.sender_id == mid) & (TrainerMessage.recipient_id == current.id))
        ).order_by(TrainerMessage.created_at.desc()).first()
        unread = db.session.query(TrainerMessage).filter(
            TrainerMessage.sender_id == mid,
            TrainerMessage.recipient_id == current.id,
            TrainerMessage.read_at.is_(None)
        ).count()
        threads.append({
            'user_id': member.id,
            'username': member.username,
            'last_message': last_msg.body[:80] + '...' if last_msg and len(last_msg.body) > 80 else (last_msg.body if last_msg else None),
            'last_at': last_msg.created_at.isoformat() if last_msg else None,
            'unread_count': unread
        })

    # Sort by last_at desc
    threads.sort(key=lambda t: t['last_at'] or '', reverse=True)
    return jsonify({'threads': threads}), 200


@messages_bp.route('/thread/<int:other_user_id>', methods=['GET'])
@jwt_required()
def get_thread(other_user_id):
    """Get messages between current user and other_user_id."""
    db = _get_db()
    User = _get_user_model()
    TrainerMessage = _get_trainer_message_model()

    current = _get_current_user()
    if not current:
        return jsonify({'error': 'Invalid token'}), 401

    other = db.session.get(User, other_user_id)
    if not other:
        return jsonify({'error': 'User not found'}), 404

    # Member: can only thread with assigned_to
    if current.role == 'member':
        if getattr(current, 'assigned_to', None) != other_user_id:
            return jsonify({'error': 'You can only message your assigned trainer'}), 403
    else:
        # Admin/assistant: can only thread with their members
        if other.role != 'member':
            return jsonify({'error': 'Invalid conversation'}), 403
        if current.role == 'assistant' and getattr(other, 'assigned_to', None) != current.id:
            return jsonify({'error': 'You can only message your assigned members'}), 403

    messages = db.session.query(TrainerMessage).filter(
        ((TrainerMessage.sender_id == current.id) & (TrainerMessage.recipient_id == other_user_id)) |
        ((TrainerMessage.sender_id == other_user_id) & (TrainerMessage.recipient_id == current.id))
    ).order_by(TrainerMessage.created_at.asc()).all()

    # Mark received messages as read (messages sent to current user)
    for m in messages:
        if m.recipient_id == current.id and m.read_at is None:
            m.read_at = datetime.utcnow()
    db.session.commit()

    list_out = []
    for m in messages:
        list_out.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'recipient_id': m.recipient_id,
            'body': m.body,
            'created_at': m.created_at.isoformat() if m.created_at else None,
            'read_at': m.read_at.isoformat() if m.read_at else None,
            'is_mine': m.sender_id == current.id
        })

    return jsonify({
        'other_user': {'id': other.id, 'username': other.username},
        'messages': list_out
    }), 200


@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message. Body: { "recipient_id": int, "body": str }. Member can omit recipient_id (uses assigned_to)."""
    current = _get_current_user()
    if not current:
        return jsonify({'error': 'Invalid token'}), 401

    db = _get_db()
    User = _get_user_model()
    TrainerMessage = _get_trainer_message_model()

    data = request.get_json()
    if not data or not data.get('body', '').strip():
        return jsonify({'error': 'Message body is required'}), 400

    body = data.get('body', '').strip()
    recipient_id = data.get('recipient_id')

    if current.role == 'member':
        recipient_id = getattr(current, 'assigned_to', None)
        if not recipient_id:
            return jsonify({'error': 'No trainer assigned. You cannot send messages yet.'}), 403
    else:
        if not recipient_id:
            return jsonify({'error': 'recipient_id is required'}), 400
        # Admin/assistant: recipient must be a member they train
        recipient = db.session.get(User, recipient_id)
        if not recipient or recipient.role != 'member':
            return jsonify({'error': 'Invalid recipient'}), 400
        if current.role == 'assistant' and getattr(recipient, 'assigned_to', None) != current.id:
            return jsonify({'error': 'You can only message your assigned members'}), 403

    recipient_user = db.session.get(User, recipient_id)
    if not recipient_user:
        return jsonify({'error': 'Recipient not found'}), 404

    msg = TrainerMessage(
        sender_id=current.id,
        recipient_id=recipient_id,
        body=body
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        'id': msg.id,
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
        'body': msg.body,
        'created_at': msg.created_at.isoformat() if msg.created_at else None,
        'read_at': None
    }), 201
