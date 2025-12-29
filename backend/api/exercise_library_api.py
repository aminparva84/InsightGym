"""
Public API for Exercise Library
Allows users and AI agents to search and retrieve exercises
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exercise, UserProfile
import json

exercise_library_bp = Blueprint('exercise_library', __name__, url_prefix='/api/exercises')

@exercise_library_bp.route('/library', methods=['GET'])
@jwt_required()
def get_exercise_library():
    """Get exercises from library with optional filters"""
    user_id = get_jwt_identity()
    user_language = 'fa'  # Default, can be fetched from user profile
    
    # Get query parameters
    category = request.args.get('category')
    level = request.args.get('level')
    intensity = request.args.get('intensity')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Build query
    query = Exercise.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if intensity:
        query = query.filter_by(intensity=intensity)
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    exercises = pagination.items
    
    return jsonify({
        'exercises': [ex.to_dict(user_language) for ex in exercises],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@exercise_library_bp.route('/search', methods=['GET'])
@jwt_required()
def search_exercises():
    """Search exercises with advanced filters including injury exclusions"""
    user_id = get_jwt_identity()
    user_language = 'fa'
    
    # Get user profile for injury filtering
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    user_injuries = []
    if user_profile:
        user_injuries = user_profile.get_injuries()
    
    # Get query parameters
    category = request.args.get('category')
    level = request.args.get('level')
    target_muscle = request.args.get('target_muscle')
    exclude_injuries = request.args.getlist('exclude_injuries')  # Can be multiple
    limit = request.args.get('limit', 50, type=int)
    
    # Build query
    query = Exercise.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if target_muscle:
        query = query.filter(
            (Exercise.target_muscle_fa.contains(target_muscle)) |
            (Exercise.target_muscle_en.contains(target_muscle))
        )
    
    # Exclude exercises with specified injuries
    injuries_to_exclude = exclude_injuries if exclude_injuries else user_injuries
    if injuries_to_exclude:
        for injury in injuries_to_exclude:
            # Filter out exercises that have this injury in contraindications
            query = query.filter(
                ~Exercise.injury_contraindications.contains(f'"{injury}"')
            )
    
    exercises = query.limit(limit).all()
    
    return jsonify({
        'exercises': [ex.to_dict(user_language) for ex in exercises],
        'count': len(exercises)
    }), 200

@exercise_library_bp.route('/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise_by_id(exercise_id):
    """Get a single exercise by ID"""
    user_id = get_jwt_identity()
    user_language = 'fa'
    
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify(exercise.to_dict(user_language)), 200

@exercise_library_bp.route('/recommended', methods=['GET'])
@jwt_required()
def get_recommended_exercises():
    """Get recommended exercises based on user profile"""
    user_id = get_jwt_identity()
    user_language = 'fa'
    
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not user_profile:
        return jsonify({'error': 'User profile not found'}), 404
    
    # Build query based on user profile
    query = Exercise.query
    
    # Filter by equipment access
    if not user_profile.gym_access:
        query = query.filter_by(category='functional_home')
    
    # Filter by training level
    if user_profile.training_level:
        if user_profile.training_level == 'beginner':
            query = query.filter_by(level='beginner')
        elif user_profile.training_level == 'intermediate':
            query = query.filter(Exercise.level.in_(['beginner', 'intermediate']))
    
    # Filter out exercises with user's injuries
    user_injuries = user_profile.get_injuries()
    if user_injuries:
        for injury in user_injuries:
            query = query.filter(
                ~Exercise.injury_contraindications.contains(f'"{injury}"')
            )
    
    # Filter by gender
    if user_profile.gender:
        if user_profile.gender.lower() in ['male', 'female']:
            query = query.filter(
                (Exercise.gender_suitability == user_profile.gender.lower()) |
                (Exercise.gender_suitability == 'both')
            )
    
    exercises = query.limit(20).all()
    
    return jsonify({
        'exercises': [ex.to_dict(user_language) for ex in exercises],
        'count': len(exercises)
    }), 200



