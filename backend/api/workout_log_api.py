"""
API endpoints for Workout Log and Adaptive Feedback
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exercise
from models_workout_log import WorkoutLog, ProgressEntry, WeeklyGoal, WorkoutReminder
from services.adaptive_feedback import AdaptiveFeedbackService
from datetime import datetime, timedelta, date, time
import json

workout_log_bp = Blueprint('workout_log', __name__, url_prefix='/api/workout-log')

@workout_log_bp.route('/log', methods=['POST'])
@jwt_required()
def log_workout():
    """Log a completed workout with feedback"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Required fields
        exercise_id = data.get('exercise_id')
        sets_completed = data.get('sets_completed')
        reps_completed = data.get('reps_completed')
        
        if not exercise_id or sets_completed is None or reps_completed is None:
            return jsonify({'error': 'exercise_id, sets_completed, and reps_completed are required'}), 400
        
        # Optional fields
        difficulty_rating = data.get('difficulty_rating')  # 'too_easy', 'just_right', 'too_difficult'
        pain_reported = data.get('pain_reported', False)
        pain_location = data.get('pain_location')
        form_rating = data.get('form_rating')  # 1-5
        weight_kg = data.get('weight_kg')
        duration_minutes = data.get('duration_minutes')
        distance_km = data.get('distance_km')
        notes = data.get('notes')
        language = data.get('language', 'fa')
        
        # Use adaptive feedback service
        feedback_service = AdaptiveFeedbackService(user_id, language)
        result = feedback_service.log_workout_with_feedback(
            exercise_id=exercise_id,
            sets_completed=sets_completed,
            reps_completed=reps_completed,
            difficulty_rating=difficulty_rating,
            pain_reported=pain_reported,
            pain_location=pain_location,
            form_rating=form_rating,
            weight_kg=weight_kg,
            notes=notes
        )
        
        # Add additional fields if provided
        if duration_minutes or distance_km:
            workout_log = WorkoutLog.query.get(result['workout_log_id'])
            if workout_log:
                if duration_minutes:
                    workout_log.duration_minutes = duration_minutes
                if distance_km:
                    workout_log.distance_km = distance_km
                db.session.commit()
        
        return jsonify({
            'success': True,
            'workout_log': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/history', methods=['GET'])
@jwt_required()
def get_workout_history():
    """Get user's workout history"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        exercise_id = request.args.get('exercise_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        query = WorkoutLog.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(WorkoutLog.workout_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(WorkoutLog.workout_date <= datetime.fromisoformat(end_date))
        if exercise_id:
            query = query.filter(WorkoutLog.exercise_id == exercise_id)
        
        logs = query.order_by(WorkoutLog.workout_date.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'workout_logs': [{
                'id': log.id,
                'exercise_id': log.exercise_id,
                'exercise_name_fa': log.exercise_name_fa,
                'exercise_name_en': log.exercise_name_en,
                'sets_completed': log.sets_completed,
                'reps_completed': log.reps_completed,
                'weight_kg': log.weight_kg,
                'difficulty_rating': log.difficulty_rating,
                'pain_reported': log.pain_reported,
                'pain_location': log.pain_location,
                'form_rating': log.form_rating,
                'workout_date': log.workout_date.isoformat(),
                'alternative_exercise_id': log.alternative_exercise_id,
                'alternative_reason_fa': log.alternative_reason_fa,
                'alternative_reason_en': log.alternative_reason_en
            } for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/progress', methods=['POST'])
@jwt_required()
def log_progress():
    """Log progress entry (weight, measurements, form level)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get db instance from current_app to ensure proper Flask app context
        current_db = current_app.extensions['sqlalchemy']
        
        # Update user profile weight if provided
        if data.get('weight_kg'):
            try:
                # Import UserProfile inside the route to ensure proper app context
                from models import UserProfile
                profile = current_db.session.query(UserProfile).filter_by(user_id=user_id).first()
                if profile:
                    profile.weight = data.get('weight_kg')
                    current_db.session.flush()  # Save but don't commit yet
            except Exception as e:
                import traceback
                print(f"Error updating user profile weight: {e}")
                print(traceback.format_exc())
        
        progress = ProgressEntry(
            user_id=user_id,
            weight_kg=data.get('weight_kg'),
            chest_cm=data.get('chest_cm'),
            waist_cm=data.get('waist_cm'),
            hips_cm=data.get('hips_cm'),
            arm_left_cm=data.get('arm_left_cm'),
            arm_right_cm=data.get('arm_right_cm'),
            thigh_left_cm=data.get('thigh_left_cm'),
            thigh_right_cm=data.get('thigh_right_cm'),
            form_level=data.get('form_level'),
            form_notes_fa=data.get('form_notes_fa'),
            form_notes_en=data.get('form_notes_en'),
            body_fat_percentage=data.get('body_fat_percentage'),
            muscle_mass_kg=data.get('muscle_mass_kg')
        )
        
        current_db.session.add(progress)
        current_db.session.commit()
        
        return jsonify({
            'success': True,
            'progress_entry_id': progress.id
        }), 201
        
    except Exception as e:
        try:
            current_db = current_app.extensions['sqlalchemy']
            current_db.session.rollback()
        except:
            pass
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """Get user's progress history"""
    try:
        user_id = get_jwt_identity()
        current_db = current_app.extensions['sqlalchemy']
        
        limit = request.args.get('limit', 30, type=int)
        entries = current_db.session.query(ProgressEntry).filter_by(user_id=user_id)\
            .order_by(ProgressEntry.recorded_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'progress_entries': [{
                'id': entry.id,
                'weight_kg': entry.weight_kg,
                'chest_cm': entry.chest_cm,
                'waist_cm': entry.waist_cm,
                'hips_cm': entry.hips_cm,
                'arm_left_cm': entry.arm_left_cm,
                'arm_right_cm': entry.arm_right_cm,
                'thigh_left_cm': entry.thigh_left_cm,
                'thigh_right_cm': entry.thigh_right_cm,
                'form_level': entry.form_level,
                'body_fat_percentage': entry.body_fat_percentage,
                'muscle_mass_kg': entry.muscle_mass_kg,
                'recorded_at': entry.recorded_at.isoformat()
            } for entry in entries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/goals', methods=['POST'])
@jwt_required()
def create_weekly_goal():
    """Create a weekly goal"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Calculate week dates
        week_start = datetime.fromisoformat(data.get('week_start_date')).date()
        week_end = week_start + timedelta(days=6)
        
        goal = WeeklyGoal(
            user_id=user_id,
            week_start_date=week_start,
            week_end_date=week_end,
            workout_days_target=data.get('workout_days_target', 3),
            target_weight_kg=data.get('target_weight_kg'),
            notes_fa=data.get('notes_fa'),
            notes_en=data.get('notes_en')
        )
        
        # Set exercise goals if provided
        if data.get('exercise_goals'):
            goal.set_exercise_goals(data['exercise_goals'])
        
        # Set target measurements if provided
        if data.get('target_measurements'):
            goal.set_target_measurements(data['target_measurements'])
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'goal_id': goal.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/goals', methods=['GET'])
@jwt_required()
def get_weekly_goals():
    """Get user's weekly goals"""
    try:
        user_id = get_jwt_identity()
        
        status = request.args.get('status')  # 'active', 'completed', 'failed'
        query = WeeklyGoal.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        goals = query.order_by(WeeklyGoal.week_start_date.desc()).all()
        
        return jsonify({
            'success': True,
            'goals': [{
                'id': goal.id,
                'week_start_date': goal.week_start_date.isoformat(),
                'week_end_date': goal.week_end_date.isoformat(),
                'workout_days_target': goal.workout_days_target,
                'workout_days_completed': goal.workout_days_completed,
                'exercise_goals': goal.get_exercise_goals(),
                'target_weight_kg': goal.target_weight_kg,
                'target_measurements': goal.get_target_measurements(),
                'status': goal.status,
                'completion_percentage': goal.completion_percentage,
                'notes_fa': goal.notes_fa,
                'notes_en': goal.notes_en
            } for goal in goals]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/goals/<int:goal_id>/update', methods=['PUT'])
@jwt_required()
def update_weekly_goal(goal_id):
    """Update weekly goal progress"""
    try:
        user_id = get_jwt_identity()
        goal = WeeklyGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        
        data = request.get_json()
        
        # Update workout days completed
        if 'workout_days_completed' in data:
            goal.workout_days_completed = data['workout_days_completed']
        
        # Calculate completion percentage
        if goal.workout_days_target > 0:
            goal.completion_percentage = (goal.workout_days_completed / goal.workout_days_target) * 100
        
        # Update status
        if goal.completion_percentage >= 100:
            goal.status = 'completed'
        elif goal.completion_percentage < 50:
            goal.status = 'failed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'goal': {
                'id': goal.id,
                'completion_percentage': goal.completion_percentage,
                'status': goal.status
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/reminders', methods=['POST'])
@jwt_required()
def create_reminder():
    """Create workout reminder"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        reminder_time = datetime.strptime(data.get('reminder_time'), '%H:%M').time()
        days_of_week = data.get('days_of_week', [1, 2, 3, 4, 5])  # Mon-Fri default
        
        reminder = WorkoutReminder(
            user_id=user_id,
            reminder_time=reminder_time,
            days_of_week=json.dumps(days_of_week),
            enabled=data.get('enabled', True),
            message_fa=data.get('message_fa', 'زمان تمرین شما فرا رسیده است!'),
            message_en=data.get('message_en', 'Time for your workout!'),
            timezone=data.get('timezone', 'Asia/Tehran')
        )
        
        # Calculate next send time
        reminder.next_send_at = _calculate_next_reminder_time(reminder_time, days_of_week)
        
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reminder_id': reminder.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_log_bp.route('/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    """Get user's workout reminders"""
    try:
        user_id = get_jwt_identity()
        reminders = WorkoutReminder.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'reminders': [{
                'id': reminder.id,
                'enabled': reminder.enabled,
                'reminder_time': reminder.reminder_time.strftime('%H:%M'),
                'days_of_week': reminder.get_days_of_week(),
                'message_fa': reminder.message_fa,
                'message_en': reminder.message_en,
                'next_send_at': reminder.next_send_at.isoformat() if reminder.next_send_at else None
            } for reminder in reminders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _calculate_next_reminder_time(reminder_time: time, days_of_week: list) -> datetime:
    """Calculate next reminder send time"""
    now = datetime.now()
    current_day = now.weekday()  # 0 = Monday, 6 = Sunday
    
    # Find next day in days_of_week
    for day_offset in range(7):
        check_day = (current_day + day_offset) % 7
        if check_day in days_of_week:
            next_date = now + timedelta(days=day_offset)
            if day_offset == 0 and now.time() >= reminder_time:
                # If today is in list but time has passed, move to next occurrence
                next_date += timedelta(days=7)
            return datetime.combine(next_date.date(), reminder_time)
    
    return datetime.now() + timedelta(days=1)



