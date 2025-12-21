"""
API endpoints for workout plan generation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import UserProfile, Exercise
from services.workout_plan_generator import WorkoutPlanGenerator
import json

workout_plan_bp = Blueprint('workout_plan', __name__, url_prefix='/api/workout-plan')

@workout_plan_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_workout_plan():
    """Generate 6-month personalized workout plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        language = data.get('language', 'fa')
        
        # Get user profile
        user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not user_profile:
            return jsonify({
                'error': 'User profile not found. Please complete your profile first.'
            }), 404
        
        # Get exercise pool based on user profile
        exercise_pool = _get_exercise_pool(user_profile)
        
        if not exercise_pool:
            return jsonify({
                'error': 'No suitable exercises found. Please check your profile settings.'
            }), 400
        
        # Generate plan
        generator = WorkoutPlanGenerator(user_id, language)
        plan = generator.generate_6_month_plan(exercise_pool)
        
        # Format as weekly table
        table_format = generator.format_plan_for_table(plan)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'weekly_table': table_format
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_plan_bp.route('/generate-month', methods=['POST'])
@jwt_required()
def generate_month_plan():
    """Generate workout plan for a specific month"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'month' not in data:
            return jsonify({'error': 'Month number (1-6) is required'}), 400
        
        month = int(data['month'])
        if month < 1 or month > 6:
            return jsonify({'error': 'Month must be between 1 and 6'}), 400
        
        language = data.get('language', 'fa')
        
        # Get user profile
        user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not user_profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get exercise pool
        exercise_pool = _get_exercise_pool(user_profile)
        
        # Generate plan
        generator = WorkoutPlanGenerator(user_id, language)
        
        # Generate just this month
        from services.workout_plan_generator import MONTHLY_RULES
        from datetime import datetime
        
        month_data = {
            'month_number': month,
            'month_name_fa': MONTHLY_RULES[month]['name_fa'],
            'month_name_en': MONTHLY_RULES[month]['name_en'],
            'weeks': {}
        }
        
        # Generate 4 weeks
        muscle_groups = {
            'push': ['chest', 'shoulders', 'triceps'],
            'pull': ['back', 'biceps', 'lats'],
            'legs': ['legs', 'quads', 'hamstrings', 'glutes'],
            'core': ['core', 'abs']
        }
        
        for week in range(1, 5):
            week_data = {'week_number': week, 'days': {}}
            
            for day in range(1, user_profile.workout_days_per_week + 1):
                if day == 1:
                    target_groups = muscle_groups['push']
                elif day == 2:
                    target_groups = muscle_groups['pull']
                elif day == 3:
                    target_groups = muscle_groups['legs']
                else:
                    target_groups = muscle_groups['core']
                
                selected = generator.select_exercises_for_week(
                    month, week, target_groups, exercise_pool
                )
                
                if selected:
                    workout = generator.generate_weekly_workout(
                        month, week, day, selected
                    )
                    week_data['days'][f'day_{day}'] = workout
            
            month_data['weeks'][f'week_{week}'] = week_data
        
        return jsonify({
            'success': True,
            'month_plan': month_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _get_exercise_pool(user_profile: UserProfile) -> list:
    """Get filtered exercise pool based on user profile"""
    # Base query
    query = Exercise.query
    
    # Filter by equipment
    if not user_profile.gym_access:
        query = query.filter(Exercise.category == 'functional_home')
    else:
        # Can use all categories
        pass
    
    # Filter by training level
    if user_profile.training_level:
        # For beginner, only show beginner exercises
        # For intermediate+, can show up to their level
        if user_profile.training_level == 'beginner':
            query = query.filter(Exercise.level == 'beginner')
        elif user_profile.training_level == 'intermediate':
            query = query.filter(Exercise.level.in_(['beginner', 'intermediate']))
        # Advanced can do all
    
    # Filter out exercises with user's injuries
    if user_profile.injuries:
        try:
            injuries = json.loads(user_profile.injuries) if isinstance(user_profile.injuries, str) else user_profile.injuries
        except:
            injuries = []
        
        for injury in injuries:
            # Exclude exercises that have this injury in contraindications
            query = query.filter(
                ~Exercise.injury_contraindications.contains(injury)
            )
    
    # Filter by gender if specified
    if user_profile.gender:
        if user_profile.gender.lower() in ['male', 'female']:
            query = query.filter(
                (Exercise.gender_suitability == user_profile.gender.lower()) |
                (Exercise.gender_suitability == 'both')
            )
    
    return query.all()

@workout_plan_bp.route('/rules', methods=['GET'])
def get_progression_rules():
    """Get monthly progression rules"""
    from services.workout_plan_generator import MONTHLY_RULES
    return jsonify(MONTHLY_RULES), 200

