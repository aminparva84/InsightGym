"""
Admin API for managing exercise library
Allows admins to CRUD exercises
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exercise, EXERCISE_CATEGORY_BODYBUILDING_MACHINE, EXERCISE_CATEGORY_FUNCTIONAL_HOME, EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE
from app import User  # User is defined in app.py, not models.py
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def is_admin(user_id):
    """Check if user is admin - for now, check if username is 'admin' or email contains 'admin'"""
    user = User.query.get(user_id)
    if not user:
        return False
    # Simple admin check - in production, add is_admin field to User model
    return user.username.lower() == 'admin' or 'admin' in user.email.lower()

@admin_bp.route('/exercises', methods=['GET'])
@jwt_required()
def get_all_exercises():
    """Get all exercises with pagination and filters"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get query parameters
    category = request.args.get('category')
    level = request.args.get('level')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Build query
    query = Exercise.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    exercises = pagination.items
    
    return jsonify({
        'exercises': [ex.to_dict('fa') for ex in exercises],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@admin_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise(exercise_id):
    """Get a single exercise by ID"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify(exercise.to_dict('fa')), 200

@admin_bp.route('/exercises', methods=['POST'])
@jwt_required()
def create_exercise():
    """Create a new exercise"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['category', 'name_fa', 'name_en', 'target_muscle_fa', 'target_muscle_en', 
                       'level', 'intensity', 'gender_suitability']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Handle injury_contraindications
    if 'injury_contraindications' in data and isinstance(data['injury_contraindications'], list):
        data['injury_contraindications'] = json.dumps(data['injury_contraindications'], ensure_ascii=False)
    
    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
        return jsonify(exercise.to_dict('fa')), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/exercises/<int:exercise_id>', methods=['PUT'])
@jwt_required()
def update_exercise(exercise_id):
    """Update an existing exercise"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    exercise = Exercise.query.get_or_404(exercise_id)
    data = request.get_json()
    
    # Handle injury_contraindications
    if 'injury_contraindications' in data and isinstance(data['injury_contraindications'], list):
        data['injury_contraindications'] = json.dumps(data['injury_contraindications'], ensure_ascii=False)
    
    # Update fields
    for key, value in data.items():
        if hasattr(exercise, key):
            setattr(exercise, key, value)
    
    try:
        db.session.commit()
        return jsonify(exercise.to_dict('fa')), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    """Delete an exercise"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    try:
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({'message': 'Exercise deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/exercises/bulk', methods=['POST'])
@jwt_required()
def bulk_create_exercises():
    """Bulk create exercises"""
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    exercises_data = data.get('exercises', [])
    
    if not exercises_data:
        return jsonify({'error': 'No exercises provided'}), 400
    
    created = []
    errors = []
    
    for idx, ex_data in enumerate(exercises_data):
        try:
            # Handle injury_contraindications
            if 'injury_contraindications' in ex_data and isinstance(ex_data['injury_contraindications'], list):
                ex_data['injury_contraindications'] = json.dumps(ex_data['injury_contraindications'], ensure_ascii=False)
            
            exercise = Exercise(**ex_data)
            db.session.add(exercise)
            created.append(ex_data.get('name_fa', f'Exercise {idx+1}'))
        except Exception as e:
            errors.append(f'Exercise {idx+1}: {str(e)}')
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Created {len(created)} exercises',
            'created': created,
            'errors': errors
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/check-admin', methods=['GET'])
@jwt_required()
def check_admin():
    """Check if current user is admin"""
    user_id = get_jwt_identity()
    return jsonify({'is_admin': is_admin(user_id)}), 200



