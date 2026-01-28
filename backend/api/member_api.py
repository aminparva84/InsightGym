"""
Member API: weekly goals, step counter, break requests (member-only features)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from models import (
    MemberWeeklyGoal,
    DailySteps,
    BreakRequest,
    TrainingProgram,
)

member_bp = Blueprint('member', __name__, url_prefix='/api/member')


def _get_db():
    """Get database instance from current app context (avoids SQLAlchemy instance mismatch)."""
    return current_app.extensions['sqlalchemy']


def _get_user_id():
    uid = get_jwt_identity()
    return int(uid) if uid else None


# ---------- Weekly Goals ----------
@member_bp.route('/weekly-goals', methods=['GET'])
@jwt_required()
def get_weekly_goals():
    """Get weekly mini-goals for the current member (from their training programs)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        language = request.args.get('language', 'fa')
        db = _get_db()
        goals = (
            db.session.query(MemberWeeklyGoal)
            .filter_by(user_id=user_id)
            .order_by(MemberWeeklyGoal.training_program_id, MemberWeeklyGoal.week_number)
            .all()
        )

        # If no goals exist but user has programs, seed default weekly goals
        if not goals:
            _seed_weekly_goals_for_user(user_id, language, db)
            goals = (
                db.session.query(MemberWeeklyGoal)
                .filter_by(user_id=user_id)
                .order_by(MemberWeeklyGoal.training_program_id, MemberWeeklyGoal.week_number)
                .all()
            )

        out = []
        for g in goals:
            program = db.session.get(TrainingProgram, g.training_program_id)
            program_name = (program.name_fa if language == 'fa' else program.name_en) if program else None
            out.append({
                'id': g.id,
                'user_id': g.user_id,
                'training_program_id': g.training_program_id,
                'training_program_name': program_name,
                'week_number': g.week_number,
                'goal_title': g.goal_title_fa if language == 'fa' else g.goal_title_en,
                'goal_title_fa': g.goal_title_fa,
                'goal_title_en': g.goal_title_en,
                'goal_description': (g.goal_description_fa if language == 'fa' else g.goal_description_en) or '',
                'completed': g.completed,
                'completed_at': g.completed_at.isoformat() if g.completed_at else None,
                'created_at': g.created_at.isoformat() if g.created_at else None,
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _seed_weekly_goals_for_user(user_id, language='fa', db=None):
    """Create default weekly goals for each training program the member has (user-specific + general)."""
    if db is None:
        db = _get_db()
    user_programs = db.session.query(TrainingProgram).filter_by(user_id=user_id).all()
    general_programs = db.session.query(TrainingProgram).filter(TrainingProgram.user_id.is_(None)).all()
    all_programs = user_programs + general_programs
    added = False
    for program in all_programs:
        duration = program.duration_weeks or 4
        for week in range(1, duration + 1):
            existing = (
                db.session.query(MemberWeeklyGoal)
                .filter_by(
                    user_id=user_id,
                    training_program_id=program.id,
                    week_number=week,
                )
                .first()
            )
            if existing:
                continue
            title_fa = f'هفته {week}: انجام جلسات هفته {week}'
            title_en = f'Week {week}: Complete Week {week} sessions'
            goal = MemberWeeklyGoal(
                user_id=user_id,
                training_program_id=program.id,
                week_number=week,
                goal_title_fa=title_fa,
                goal_title_en=title_en,
                goal_description_fa=None,
                goal_description_en=None,
            )
            db.session.add(goal)
            added = True
    if added:
        db.session.commit()


@member_bp.route('/weekly-goals/<int:goal_id>', methods=['PATCH'])
@jwt_required()
def update_weekly_goal(goal_id):
    """Mark a weekly goal as completed or not (member only, own goals)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        goal = db.session.query(MemberWeeklyGoal).filter_by(id=goal_id, user_id=user_id).first()
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404

        data = request.get_json() or {}
        completed = data.get('completed')
        if completed is not None:
            goal.completed = bool(completed)
            goal.completed_at = datetime.utcnow() if goal.completed else None
        db.session.commit()

        return jsonify({
            'id': goal.id,
            'completed': goal.completed,
            'completed_at': goal.completed_at.isoformat() if goal.completed_at else None,
        }), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------- Step Counter ----------
@member_bp.route('/steps', methods=['GET'])
@jwt_required()
def get_steps():
    """Get step counts for the current user. Query params: from_date, to_date (YYYY-MM-DD)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        today = date.today()
        from_date = today - timedelta(days=30)
        to_date = today
        if from_date_str:
            try:
                from_date = date.fromisoformat(from_date_str)
            except ValueError:
                pass
        if to_date_str:
            try:
                to_date = date.fromisoformat(to_date_str)
            except ValueError:
                pass

        rows = (
            db.session.query(DailySteps)
            .filter(
                DailySteps.user_id == user_id,
                DailySteps.date >= from_date,
                DailySteps.date <= to_date,
            )
            .order_by(DailySteps.date.desc())
            .all()
        )
        out = [
            {
                'id': r.id,
                'date': r.date.isoformat(),
                'steps': r.steps,
                'source': r.source,
            }
            for r in rows
        ]
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/steps', methods=['POST'])
@jwt_required()
def post_steps():
    """Record or update steps for a date. Body: { date: 'YYYY-MM-DD', steps: number, source?: 'manual'|'device' }."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        data = request.get_json()
        if not data or 'steps' not in data:
            return jsonify({'error': 'steps is required'}), 400

        steps_val = int(data.get('steps', 0))
        if steps_val < 0:
            return jsonify({'error': 'steps must be non-negative'}), 400

        date_str = data.get('date')
        if not date_str:
            target_date = date.today()
        else:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

        source = (data.get('source') or 'manual').lower()
        if source not in ('manual', 'device'):
            source = 'manual'

        row = (
            db.session.query(DailySteps)
            .filter_by(user_id=user_id, date=target_date)
            .first()
        )
        if row:
            row.steps = steps_val
            row.source = source
            row.updated_at = datetime.utcnow()
        else:
            row = DailySteps(
                user_id=user_id,
                date=target_date,
                steps=steps_val,
                source=source,
            )
            db.session.add(row)
        db.session.commit()

        return jsonify({
            'id': row.id,
            'date': row.date.isoformat(),
            'steps': row.steps,
            'source': row.source,
        }), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------- Break Request ----------
@member_bp.route('/break-request', methods=['POST'])
@jwt_required()
def create_break_request():
    """Member submits a break request (message sent to their assigned admin/assistant)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        from app import User
        user = db.session.get(User, user_id)
        if not user or user.role != 'member':
            return jsonify({'error': 'Only members can submit break requests'}), 403

        data = request.get_json()
        message = (data.get('message') or '').strip()
        if not message:
            return jsonify({'error': 'message is required'}), 400

        br = BreakRequest(
            user_id=user_id,
            message=message,
            status='pending',
        )
        db.session.add(br)
        db.session.commit()

        return jsonify({
            'id': br.id,
            'message': br.message,
            'status': br.status,
            'created_at': br.created_at.isoformat() if br.created_at else None,
        }), 201
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


@member_bp.route('/break-requests', methods=['GET'])
@jwt_required()
def list_my_break_requests():
    """Member lists their own break requests (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        rows = (
            db.session.query(BreakRequest)
            .filter_by(user_id=user_id)
            .order_by(BreakRequest.created_at.desc())
            .limit(50)
            .all()
        )
        out = [
            {
                'id': r.id,
                'message': r.message,
                'status': r.status,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'responded_at': r.responded_at.isoformat() if r.responded_at else None,
                'response_message': r.response_message,
            }
            for r in rows
        ]
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
