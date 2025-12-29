"""
API endpoints for Persian Fitness Coach AI Agent
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exercise
from services.ai_coach_agent import PersianFitnessCoachAI
from services.vectorSearchHelpers import searchExercisesWithProfile, mapUserProfileToSearchProfile
import json

ai_coach_bp = Blueprint('ai_coach', __name__, url_prefix='/api/ai-coach')

@ai_coach_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat_with_coach():
    """Chat with Persian Fitness Coach AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize AI coach
        coach = PersianFitnessCoachAI(user_id)
        
        # Try to get exercises from vector search if available
        exercise_pool = None
        try:
            # Use vector search to get relevant exercises
            user_profile_dict = mapUserProfileToSearchProfile(
                coach.user_profile.__dict__ if coach.user_profile else {}
            )
            
            # Search for exercises (broad query)
            search_results = searchExercisesWithProfile(
                'تمرینات تناسب اندام',
                user_id,
                {
                    'maxResults': 50,
                    'language': 'fa'
                }
            )
            
            # Convert to Exercise objects
            if search_results:
                exercise_ids = [r.exercise_id for r in search_results]
                exercise_pool = Exercise.query.filter(Exercise.id.in_(exercise_ids)).all()
        except Exception as e:
            print(f"Vector search error: {e}")
            # Fallback to database query
            query = Exercise.query
            if coach.user_profile and not coach.user_profile.gym_access:
                query = query.filter(Exercise.category == 'functional_home')
            exercise_pool = query.limit(50).all()
        
        # Generate response
        response = coach.generate_personalized_response(message, exercise_pool)
        
        return jsonify({
            'success': True,
            'response': response['response'],
            'metadata': {
                'injuries_detected': response.get('injuries_detected', []),
                'safety_checked': response.get('safety_checked', False),
                'exercises_suggested': response.get('exercises', []),
                'month': response.get('month')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_coach_bp.route('/workout-plan', methods=['POST'])
@jwt_required()
def generate_coach_workout_plan():
    """Generate workout plan using AI coach with Vector DB"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        month = data.get('month', 1)
        target_muscle = data.get('target_muscle')  # Optional
        language = data.get('language', 'fa')
        
        if month < 1 or month > 6:
            return jsonify({'error': 'Month must be between 1 and 6'}), 400
        
        # Initialize coach
        coach = PersianFitnessCoachAI(user_id)
        
        # Get user injuries
        user_injuries = []
        if coach.user_profile:
            user_injuries = coach.user_profile.get_injuries()
        
        # Build search query
        if target_muscle:
            query = f"تمرینات {target_muscle}"
        else:
            query = "تمرینات تناسب اندام"
        
        # Use vector search
        try:
            search_results = searchExercisesWithProfile(
                query,
                user_id,
                {
                    'maxResults': 20,
                    'language': language
                }
            )
            
            exercise_ids = [r.exercise_id for r in search_results]
            exercise_pool = Exercise.query.filter(Exercise.id.in_(exercise_ids)).all()
        except:
            # Fallback
            query = Exercise.query
            if coach.user_profile and not coach.user_profile.gym_access:
                query = query.filter(Exercise.category == 'functional_home')
            exercise_pool = query.limit(20).all()
        
        # Get safe exercises
        safe_exercises = coach.get_safe_exercises(exercise_pool, user_injuries)
        
        # Generate workout plan response
        response_data = coach._handle_workout_plan_request(
            query,
            month,
            user_injuries,
            safe_exercises
        )
        
        return jsonify({
            'success': True,
            'workout_plan': response_data['response'],
            'exercises': response_data.get('exercises', []),
            'month': month,
            'safety_checked': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



