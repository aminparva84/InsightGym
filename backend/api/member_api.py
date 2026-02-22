"""
Member API: weekly goals, step counter, break requests (member-only features)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
import json
from models import (
    MemberWeeklyGoal,
    DailySteps,
    BreakRequest,
    TrainingProgram,
    MemberTrainingActionCompletion,
    Notification,
    TrainingActionNote,
    Exercise,
    ProgressCheckRequest,
    PurchaseOrder,
)

member_bp = Blueprint('member', __name__, url_prefix='/api/member')


def _get_db():
    """Get database instance from current app context (avoids SQLAlchemy instance mismatch)."""
    return current_app.extensions.get('sqlalchemy')


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

        # During active trial, only show goals for user's own program(s)
        from app import User
        user = db.session.get(User, user_id)
        trial_ends_at = getattr(user, 'trial_ends_at', None) if user else None
        trial_active = (
            user
            and getattr(user, 'role', None) == 'member'
            and trial_ends_at
            and trial_ends_at > datetime.utcnow()
        )
        user_program_ids = set(
            p.id for p in db.session.query(TrainingProgram).filter_by(user_id=user_id).all()
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
            if trial_active and program and program.user_id != user_id:
                continue
            if user_program_ids and program and program.user_id is None:
                continue
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

    # Members should only get goals for their own program(s)
    from app import User
    user = db.session.get(User, user_id)
    if user and getattr(user, 'role', None) == 'member':
        all_programs = user_programs
    else:
        all_programs = user_programs + general_programs

    # If user is on active trial, only seed goals for their trial program(s)
    trial_ends_at = getattr(user, 'trial_ends_at', None) if user else None
    trial_active = (
        user
        and getattr(user, 'role', None) == 'member'
        and trial_ends_at
        and trial_ends_at > datetime.utcnow()
    )
    if trial_active:
        all_programs = user_programs
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


def _assign_program_after_purchase(db, user_id, program_id, language='fa'):
    """
    Assign a training program to the member after purchase.
    Tries AI-generated personalized program first (user profile + admin Training Info).
    Falls back to copying the purchased template if AI fails.
    """
    from app import User
    from models import TrainingProgram, MemberWeeklyGoal, MemberTrainingActionCompletion, TrainingActionNote

    user = db.session.get(User, user_id)
    if not user or getattr(user, 'role', None) != 'member':
        return None

    # Remove existing user programs and related rows
    existing = db.session.query(TrainingProgram).filter_by(user_id=user_id).all()
    for prog in existing:
        pid = prog.id
        db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
        db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
        db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
        db.session.delete(prog)

    template = db.session.get(TrainingProgram, program_id)
    if not template:
        template = (
            db.session.query(TrainingProgram)
            .filter(TrainingProgram.user_id.is_(None))
            .order_by(TrainingProgram.id)
            .first()
        )
    if not template:
        return None

    # Try AI-generated personalized program first
    from services.session_ai_service import generate_personalized_program_after_purchase
    from services.ai_debug_logger import append_ai_program_log
    from models import UserProfile

    lang = getattr(user, 'language', language) or language
    sessions, ai_error = generate_personalized_program_after_purchase(user_id, program_id, lang, db)

    # Build profile summary and purpose for logging
    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    parts = []
    if profile:
        if profile.training_level:
            parts.append(f"training_level={profile.training_level}")
        if profile.workout_days_per_week:
            parts.append(f"workout_days_per_week={profile.workout_days_per_week}")
        if profile.get_fitness_goals():
            parts.append("fitness_goals=" + ",".join(profile.get_fitness_goals()))
    profile_summary = "; ".join(parts) if parts else "default"
    goals = profile.get_fitness_goals() if profile and hasattr(profile, 'get_fitness_goals') else []
    purpose = "gain_muscle"
    goal_to_purpose = {
        "lose_weight": "lose_weight", "weight_loss": "lose_weight",
        "gain_muscle": "gain_muscle", "muscle_gain": "gain_muscle", "strength": "gain_muscle",
        "gain_weight": "gain_weight", "shape_fitting": "shape_fitting", "endurance": "shape_fitting",
    }
    for g in (goals or []):
        g_lower = (g or "").strip().lower()
        if g_lower in goal_to_purpose:
            purpose = goal_to_purpose[g_lower]
            break

    if sessions:
        copy_program = TrainingProgram(
            user_id=user_id,
            name_fa=template.name_fa,
            name_en=template.name_en,
            description_fa=template.description_fa,
            description_en=template.description_en,
            duration_weeks=template.duration_weeks,
            training_level=template.training_level,
            category=template.category,
            sessions=None,
        )
        copy_program.set_sessions(sessions)
        db.session.add(copy_program)
    else:
        # Fallback: copy template and inject warming/cooldown from admin
        template_sessions = template.get_sessions() if hasattr(template, 'get_sessions') else []
        if isinstance(template_sessions, list):
            from services.session_ai_service import _inject_session_phases
            for s in template_sessions:
                if isinstance(s, dict):
                    _inject_session_phases(s, db)
        copy_program = TrainingProgram(
            user_id=user_id,
            name_fa=template.name_fa,
            name_en=template.name_en,
            description_fa=template.description_fa,
            description_en=template.description_en,
            duration_weeks=template.duration_weeks,
            training_level=template.training_level,
            category=template.category,
            sessions=json.dumps(template_sessions, ensure_ascii=False) if template_sessions else template.sessions,
        )
        db.session.add(copy_program)

    db.session.flush()
    assigned_id = copy_program.id if copy_program else 0
    append_ai_program_log(
        action="ai_generated" if sessions else "template_copy",
        user_id=user_id,
        program_id=program_id,
        template_name=(template.name_fa or template.name_en or ""),
        purpose=purpose,
        profile_summary=profile_summary,
        sessions_count=len(sessions) if sessions else 0,
        assigned_program_id=assigned_id,
        error="" if sessions else (ai_error or "AI returned no sessions; fallback to template"),
    )
    _seed_weekly_goals_for_user(user_id, language, db)
    return copy_program


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


# ---------- Purchase training program ----------
@member_bp.route('/purchase-training-program', methods=['POST'])
@jwt_required()
def purchase_training_program():
    """Create a purchase order and assign program if paid (no gateway yet)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        data = request.get_json() or {}
        program_id = data.get('program_id')
        packages = data.get('packages') or []
        ems_form = data.get('ems_form') or {}
        discount_code = (data.get('discount_code') or '').strip()
        language = data.get('language') or 'fa'

        if not program_id:
            return jsonify({'error': 'program_id required'}), 400

        def _sum_prices(items):
            total = 0.0
            for item in items:
                try:
                    total += float(item.get('price', 0))
                except Exception:
                    pass
            return total

        base_price = float(data.get('base_price') or 0)
        packages_total = _sum_prices(packages)
        subtotal = base_price + packages_total

        if discount_code.lower() == 'free100':
            discount_amount = subtotal
            total = 0.0
            status = 'paid'
        else:
            discount_amount = 0.0
            total = subtotal
            status = 'pending_payment'

        db = _get_db()
        # Ensure purchase_orders table exists (especially after code update)
        try:
            PurchaseOrder.__table__.create(db.engine, checkfirst=True)
        except Exception as create_err:
            return jsonify({'error': f'Failed to ensure purchase_orders table: {create_err}'}), 500
        order = PurchaseOrder(
            user_id=user_id,
            program_id=int(program_id),
            packages_json=json.dumps(packages, ensure_ascii=False),
            ems_form_json=json.dumps(ems_form, ensure_ascii=False) if ems_form else None,
            discount_code=discount_code or None,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            status=status,
            paid_at=datetime.utcnow() if status == 'paid' else None,
        )
        db.session.add(order)

        assigned_program_id = None
        if status == 'paid':
            program = _assign_program_after_purchase(db, user_id, int(program_id), language)
            assigned_program_id = program.id if program else None

        db.session.commit()
        return jsonify({
            'order_id': order.id,
            'status': order.status,
            'total': order.total,
            'assigned_program_id': assigned_program_id,
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


# ---------- Training action progress (tick completed exercises) ----------
@member_bp.route('/training-progress', methods=['GET'])
@jwt_required()
def get_training_progress():
    """Get completed action keys for the member. Query: program_id (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        program_id = request.args.get('program_id', type=int)
        q = db.session.query(MemberTrainingActionCompletion).filter_by(user_id=user_id)
        if program_id is not None:
            q = q.filter_by(training_program_id=program_id)
        rows = q.all()
        out = [
            {
                'training_program_id': r.training_program_id,
                'session_index': r.session_index,
                'exercise_index': r.exercise_index,
                'completed_at': r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in rows
        ]
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/training-progress', methods=['POST'])
@jwt_required()
def toggle_training_progress():
    """Mark an action as completed or not. Body: { program_id, session_index, exercise_index, completed: true|false }."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        data = request.get_json()
        if not data or 'program_id' not in data or 'session_index' not in data or 'exercise_index' not in data:
            return jsonify({'error': 'program_id, session_index, exercise_index required'}), 400

        program_id = int(data['program_id'])
        session_index = int(data['session_index'])
        exercise_index = int(data['exercise_index'])
        completed = data.get('completed', True)

        existing = (
            db.session.query(MemberTrainingActionCompletion)
            .filter_by(
                user_id=user_id,
                training_program_id=program_id,
                session_index=session_index,
                exercise_index=exercise_index,
            )
            .first()
        )

        if completed:
            if not existing:
                row = MemberTrainingActionCompletion(
                    user_id=user_id,
                    training_program_id=program_id,
                    session_index=session_index,
                    exercise_index=exercise_index,
                )
                db.session.add(row)
            else:
                row = existing
        else:
            if existing:
                db.session.delete(existing)
            row = None

        db.session.commit()

        if row:
            return jsonify({
                'training_program_id': row.training_program_id,
                'session_index': row.session_index,
                'exercise_index': row.exercise_index,
                'completed': True,
                'completed_at': row.completed_at.isoformat() if row.completed_at else None,
            }), 200
        return jsonify({
            'training_program_id': program_id,
            'session_index': session_index,
            'exercise_index': exercise_index,
            'completed': False,
        }), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------- Notifications (trainer notes etc.) ----------
@member_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """List notifications for the current user. Query: unread_only (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        if not db:
            return jsonify({'error': 'Database not available'}), 500

        language = request.args.get('language', 'fa')
        unread_only = request.args.get('unread_only', '').lower() == 'true'

        try:
            q = db.session.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc())
            if unread_only:
                q = q.filter(Notification.read_at.is_(None))
            rows = q.limit(100).all()
        except Exception as table_err:
            # Table might not exist yet (migration not run); return empty list so UI works
            import traceback
            print(f"[member/notifications] Query failed (table may not exist): {table_err}")
            traceback.print_exc()
            return jsonify([]), 200

        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'title': r.title_fa if language == 'fa' else r.title_en,
                'body': (r.body_fa if language == 'fa' else r.body_en) or '',
                'type': r.type,
                'link': r.link or '',
                'voice_url': r.voice_url or '',
                'read_at': r.read_at.isoformat() if r.read_at else None,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            })
        return jsonify(out), 200
    except Exception as e:
        import traceback
        print(f"[member/notifications] Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@member_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        n = db.session.query(Notification).filter_by(id=notification_id, user_id=user_id).first()
        if not n:
            return jsonify({'error': 'Notification not found'}), 404

        n.read_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'id': n.id, 'read_at': n.read_at.isoformat()}), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


@member_bp.route('/notifications/read-all', methods=['PATCH'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for the current user."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        db.session.query(Notification).filter_by(user_id=user_id).filter(Notification.read_at.is_(None)).update({'read_at': datetime.utcnow()})
        db.session.commit()
        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------- 7-day free trial ----------
@member_bp.route('/trial-status', methods=['GET'])
@jwt_required()
def get_trial_status():
    """
    Get current member's trial status. Creates a 'trial_ended' notification once when trial has ended.
    Returns: trial_ends_at, is_trial_active, days_left, trial_ended.
    """
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        from app import User
        db = _get_db()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        trial_ends_at = getattr(user, 'trial_ends_at', None)
        now = datetime.utcnow()
        is_trial_active = trial_ends_at is not None and trial_ends_at > now
        trial_ended = trial_ends_at is not None and trial_ends_at <= now

        if trial_ended:
            # Ensure we send trial-ended notification once
            existing = db.session.query(Notification).filter_by(
                user_id=user_id, type='trial_ended'
            ).first()
            if not existing:
                lang = getattr(user, 'language', 'fa') or 'fa'
                n = Notification(
                    user_id=user_id,
                    title_fa='پایان دوره آزمایشی',
                    title_en='Free trial ended',
                    body_fa='دوره ۷ روزه رایگان شما به پایان رسید. برای ادامه استفاده از تمام امکانات تمرینی، اشتراک تهیه کنید.',
                    body_en='Your 7-day free trial has ended. Subscribe to continue using all training features.',
                    type='trial_ended',
                    link='?tab=profile',
                )
                db.session.add(n)
                db.session.commit()

        days_left = None
        if trial_ends_at and is_trial_active:
            delta = trial_ends_at - now
            days_left = max(0, delta.days) if delta.days else 0

        return jsonify({
            'trial_ends_at': trial_ends_at.isoformat() if trial_ends_at else None,
            'is_trial_active': is_trial_active,
            'days_left': days_left,
            'trial_ended': trial_ended,
        }), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------- Trainer notes for current action (member view) ----------
@member_bp.route('/action-notes', methods=['GET'])
@jwt_required()
def get_action_notes_for_member():
    """Get trainer notes for a program (all session+exercise notes). Query: program_id."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        program_id = request.args.get('program_id', type=int)
        if program_id is None:
            return jsonify({'error': 'program_id required'}), 400

        db = _get_db()
        rows = (
            db.session.query(TrainingActionNote)
            .filter_by(training_program_id=program_id)
            .all()
        )
        language = request.args.get('language', 'fa')
        out = []
        for r in rows:
            out.append({
                'session_index': r.session_index,
                'exercise_index': r.exercise_index,
                'note': (r.note_fa if language == 'fa' else r.note_en) or '',
                'voice_url': r.voice_url or '',
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/progress-check-request', methods=['POST'])
@jwt_required()
def create_progress_check_request():
    """Member requests a progress check from trainer (accept/deny by trainer)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        db = _get_db()
        req = ProgressCheckRequest(member_id=user_id, status='pending')
        db.session.add(req)
        db.session.commit()
        return jsonify({
            'id': req.id,
            'status': req.status,
            'requested_at': req.requested_at.isoformat() if req.requested_at else None,
            'message': 'Progress check requested. Your trainer will respond shortly.'
        }), 201
    except Exception as e:
        db = _get_db()
        if db:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500


@member_bp.route('/progress-check-requests', methods=['GET'])
@jwt_required()
def list_my_progress_check_requests():
    """Member lists their own progress check requests."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        db = _get_db()
        rows = (
            db.session.query(ProgressCheckRequest)
            .filter_by(member_id=user_id)
            .order_by(ProgressCheckRequest.requested_at.desc())
            .limit(20)
            .all()
        )
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'status': r.status,
                'requested_at': r.requested_at.isoformat() if r.requested_at else None,
                'responded_at': r.responded_at.isoformat() if r.responded_at else None,
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/session-phases', methods=['GET'])
@jwt_required()
def get_session_phases():
    """Get warming, cooldown, ending message content for training session steps (from site settings)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        db = _get_db()
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        raw = (getattr(row, 'session_phases_json', None) or '').strip() if row else ''
        if not raw:
            return jsonify({
                'warming': {'title_fa': '', 'title_en': '', 'steps': []},
                'cooldown': {'title_fa': '', 'title_en': '', 'steps': []},
                'ending_message_fa': '',
                'ending_message_en': ''
            }), 200
        import json
        data = json.loads(raw)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/exercise-info', methods=['GET'])
@jwt_required()
def get_exercise_info_by_name():
    """Get movement info (video, voice, trainer notes) for an exercise by name. Query: name_fa, name_en (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        name_fa = (request.args.get('name_fa') or '').strip()
        name_en = (request.args.get('name_en') or '').strip()
        if not name_fa and not name_en:
            return jsonify({'error': 'name_fa or name_en required'}), 400

        db = _get_db()
        q = db.session.query(Exercise)
        if name_fa and name_en:
            ex = q.filter((Exercise.name_fa == name_fa) | (Exercise.name_en == name_en)).first()
        elif name_fa:
            ex = q.filter_by(name_fa=name_fa).first()
        else:
            ex = q.filter_by(name_en=name_en).first()

        if not ex:
            return jsonify({'video_url': '', 'voice_url': '', 'trainer_notes': '', 'note_notify_at_seconds': None, 'ask_post_set_questions': False, 'target_muscle': ''}), 200

        language = request.args.get('language', 'fa')
        return jsonify({
            'id': ex.id,
            'name_fa': ex.name_fa,
            'name_en': ex.name_en,
            'video_url': ex.video_url or '',
            'voice_url': ex.voice_url or '',
            'trainer_notes': (ex.trainer_notes_fa if language == 'fa' else ex.trainer_notes_en) or '',
            'note_notify_at_seconds': getattr(ex, 'note_notify_at_seconds', None),
            'ask_post_set_questions': getattr(ex, 'ask_post_set_questions', False),
            'target_muscle': (ex.target_muscle_fa if language == 'fa' else ex.target_muscle_en) or '',
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- Session AI: adapt by mood, end message, post-set feedback ----------
def _get_member_program(user_id, program_id):
    """Return TrainingProgram if it belongs to this member."""
    db = _get_db()
    return db.session.query(TrainingProgram).filter_by(id=program_id, user_id=user_id).first()


@member_bp.route('/programs/<int:program_id>/generate-sessions', methods=['POST'])
@jwt_required()
def generate_next_sessions(program_id):
    """
    Generate the next session(s) for a member's program.
    Body: { start_session_index?: number, count?: 1|2 } - count=1 for background (next session only), count=2 for manual load.
    Returns: { sessions: [...], program: {...} } or error.
    """
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        data = request.get_json() or {}
        start_session_index = data.get('start_session_index')
        count = data.get('count', 2)
        count = 1 if count == 1 else 2
        language = data.get('language') or 'fa'

        program = _get_member_program(user_id, program_id)
        if not program:
            return jsonify({'error': 'Program not found'}), 404

        sessions_list = program.get_sessions() or []
        if start_session_index is None:
            start_session_index = len(sessions_list)

        if start_session_index < 0:
            return jsonify({'error': 'Invalid start_session_index'}), 400

        # Need previous session for context when not at the beginning
        previous_session = None
        if start_session_index > 0:
            if start_session_index > len(sessions_list):
                return jsonify({
                    'error': 'Cannot generate: previous sessions missing. Generate in order (e.g. complete session 1 before generating 2-3).',
                }), 400
            previous_session = sessions_list[start_session_index - 1]

        # Get template program_id for AI config (use purchased template if available)
        template_id = program_id
        db = _get_db()
        from app import User
        user = db.session.get(User, user_id) if db else None
        lang = (user.language if user and user.language else language) or language

        from services.session_ai_service import generate_sessions_for_position
        from services.ai_debug_logger import append_ai_program_log

        new_sessions, ai_error = generate_sessions_for_position(
            user_id=user_id,
            program_id=template_id,
            start_session_index=start_session_index,
            previous_session=previous_session,
            language=lang,
            db=db,
            count=count,
        )

        if not new_sessions:
            append_ai_program_log(
                action="generate_next_sessions_failed",
                user_id=user_id,
                program_id=program_id,
                start_session_index=start_session_index,
                error=ai_error or "AI returned no sessions",
            )
            return jsonify({'error': ai_error or 'AI could not generate sessions'}), 500

        # Append new sessions to program
        updated_sessions = sessions_list + new_sessions
        program.set_sessions(updated_sessions)
        db.session.commit()

        append_ai_program_log(
            action="generate_next_sessions",
            user_id=user_id,
            program_id=program_id,
            start_session_index=start_session_index,
            sessions_count=len(new_sessions),
        )

        return jsonify({
            'sessions': new_sessions,
            'program': program.to_dict(lang),
        }), 200
    except Exception as e:
        import traceback
        print(f"[generate_next_sessions] Error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@member_bp.route('/training-programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def cancel_training_plan(program_id):
    """Cancel (delete) the member's own training plan. Only programs owned by the current user can be cancelled."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        db = _get_db()
        program = _get_member_program(user_id, program_id)
        if not program:
            return jsonify({'error': 'Program not found or you cannot cancel this plan'}), 404

        from models import MemberWeeklyGoal, MemberTrainingActionCompletion, TrainingActionNote

        pid = program.id
        db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
        db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
        db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
        db.session.delete(program)
        db.session.commit()
        return jsonify({'message': 'Plan cancelled'}), 200
    except Exception as e:
        _get_db().session.rollback()
        return jsonify({'error': str(e)}), 500


@member_bp.route('/adapt-session', methods=['POST'])
@jwt_required()
def adapt_session():
    """Adapt a session by mood/body or free text. Body: program_id, session_index, mood_or_message, language (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        data = request.get_json() or {}
        program_id = data.get('program_id')
        session_index = data.get('session_index', 0)
        mood_or_message = (data.get('mood_or_message') or '').strip()
        language = data.get('language') or 'fa'
        if program_id is None:
            return jsonify({'error': 'program_id required'}), 400
        program = _get_member_program(user_id, int(program_id))
        if not program:
            return jsonify({'error': 'Program not found'}), 404
        sessions_list = program.get_sessions()
        if session_index < 0 or session_index >= len(sessions_list):
            return jsonify({'error': 'Invalid session_index'}), 400
        session_obj = sessions_list[session_index]
        from services.session_ai_service import adapt_session_by_mood
        result = adapt_session_by_mood(session_obj, mood_or_message, language)
        adapted_exercises = result.get('exercises', session_obj.get('exercises', []))
        extra_advice = result.get('extra_advice', '')
        try:
            from services.ai_debug_logger import append_log
            append_log(
                message=f"Mood adapt | user_id={user_id} program_id={program_id} session_index={session_index} mood={mood_or_message[:100]}",
                response=extra_advice[:200] if extra_advice else "Session adapted (sets/reps adjusted)",
                action_json={
                    "action": "adapt_session_by_mood",
                    "user_id": user_id,
                    "program_id": program_id,
                    "session_index": session_index,
                    "mood_or_message": mood_or_message[:200],
                    "exercises_count": len(adapted_exercises),
                    "has_extra_advice": bool(extra_advice),
                },
                error="",
            )
        except Exception:
            pass
        return jsonify({
            'session': {**session_obj, 'exercises': adapted_exercises},
            'extra_advice': extra_advice,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/session-end-message', methods=['POST'])
@jwt_required()
def session_end_message():
    """Get AI-generated encouraging message after session end."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        data = request.get_json() or {}
        language = data.get('language') or 'fa'
        session_name = data.get('session_name') or ''
        from services.session_ai_service import get_session_end_encouragement
        message = get_session_end_encouragement(language, session_name)
        return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@member_bp.route('/post-set-feedback', methods=['POST'])
@jwt_required()
def post_set_feedback():
    """Get AI feedback after a set. Body: exercise_name_fa, exercise_name_en, target_muscle, answers (dict), language (optional)."""
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        data = request.get_json() or {}
        exercise_name_fa = (data.get('exercise_name_fa') or '').strip()
        exercise_name_en = (data.get('exercise_name_en') or '').strip()
        target_muscle = (data.get('target_muscle') or '').strip()
        answers = data.get('answers') or {}
        language = data.get('language') or 'fa'
        from services.session_ai_service import get_post_set_feedback
        feedback = get_post_set_feedback(
            exercise_name_fa, exercise_name_en, answers, target_muscle, language
        )
        return jsonify({'feedback': feedback}), 200
    except Exception as e:
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
