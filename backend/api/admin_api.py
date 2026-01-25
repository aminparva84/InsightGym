"""
Admin API for managing exercise library
Allows admins to CRUD exercises
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def get_db():
    """Get database instance from current app context"""
    return current_app.extensions.get('sqlalchemy') or current_app.extensions['sqlalchemy']

def get_user_model():
    """Get User model from app"""
    from app import User
    return User

def get_exercise_model():
    """Get Exercise model from models"""
    from models import Exercise
    return Exercise

def get_userprofile_model():
    """Get UserProfile model from models"""
    from models import UserProfile
    return UserProfile

def is_admin(user_id):
    """Check if user is admin"""
    db = get_db()
    User = get_user_model()
    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    user = db.session.get(User, user_id_int)
    if not user:
        return False
    return user.role == 'admin'

def is_admin_or_assistant(user_id):
    """Check if user is admin or assistant"""
    db = get_db()
    User = get_user_model()
    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    user = db.session.get(User, user_id_int)
    if not user:
        return False
    return user.role in ['admin', 'assistant']

@admin_bp.route('/exercises', methods=['GET'])
@jwt_required()
def get_all_exercises():
    """Get all exercises with pagination and filters"""
    db = get_db()
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get query parameters
    category = request.args.get('category')
    level = request.args.get('level')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Build query
    query = db.session.query(Exercise)
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    
    # Paginate manually
    total = query.count()
    exercises = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'exercises': [ex.to_dict('fa') for ex in exercises],
        'total': total,
        'pages': pages,
        'current_page': page
    }), 200

@admin_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise(exercise_id):
    """Get a single exercise by ID"""
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    exercise = db.session.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    return jsonify(exercise.to_dict('fa')), 200

@admin_bp.route('/exercises', methods=['POST'])
@jwt_required()
def create_exercise():
    """Create a new exercise"""
    Exercise = get_exercise_model()
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
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    exercise = db.session.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
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
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    exercise = db.session.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    
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
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    exercises_data = data.get('exercises', [])
    
    if not exercises_data:
        return jsonify({'error': 'No exercises provided'}), 400
    
    created = []
    errors = []
    
    db = get_db()
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
    try:
        db = get_db()
        User = get_user_model()
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id_int = int(user_id)
        user = db.session.get(User, user_id_int)
        
        if not user:
            return jsonify({
                'is_admin': False,
                'role': None
            }), 200
        
        return jsonify({
            'is_admin': is_admin(user_id),
            'role': user.role
        }), 200
    except Exception as e:
        import traceback
        print(f"Error in check_admin: {e}")
        print(traceback.format_exc())
        return jsonify({
            'is_admin': False,
            'role': None,
            'error': str(e)
        }), 500

# ==================== Assistant Management ====================

@admin_bp.route('/assistants', methods=['GET'])
@jwt_required()
def get_assistants():
    """Get all assistants (admin only) - shows assistants created by current admin"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    User = get_user_model()
    # Get assistants - for now, all assistants (can be filtered by created_by if needed)
    assistants = db.session.query(User).filter_by(role='assistant').all()
    assistants_data = []
    for assistant in assistants:
        profile = db.session.query(UserProfile).filter_by(user_id=assistant.id).first()
        assistants_data.append({
            'id': assistant.id,
            'username': assistant.username,
            'email': assistant.email,
            'role': assistant.role,
            'assigned_members_count': db.session.query(User).filter_by(assigned_to=assistant.id).count(),
            'profile_complete': profile is not None and profile.account_type == 'assistant',
            # Note: Password cannot be retrieved after hashing, so it's not included
            # Admin should save credentials when creating assistant
        })
    
    return jsonify(assistants_data), 200

@admin_bp.route('/assistants', methods=['POST'])
@jwt_required()
def create_assistant():
    """Create a new assistant (admin only)"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    profile_data = data.get('profile', {})  # Optional: can fill profile now or later
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    User = get_user_model()
    # Check if username/email already exists
    if db.session.query(User).filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if db.session.query(User).filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create assistant user
        assistant = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='assistant',
            language=data.get('language', 'fa')
        )
        db.session.add(assistant)
        db.session.flush()  # Get assistant ID
        
        # Create profile if data provided
        if profile_data:
            profile = UserProfile(
                user_id=assistant.id,
                account_type='assistant',
                age=profile_data.get('age'),
                weight=profile_data.get('weight'),
                height=profile_data.get('height'),
                gender=profile_data.get('gender'),
                training_level=profile_data.get('training_level'),
                exercise_history_years=profile_data.get('exercise_history_years'),
                exercise_history_description=profile_data.get('exercise_history_description'),
                chest_circumference=profile_data.get('chest_circumference'),
                waist_circumference=profile_data.get('waist_circumference'),
                abdomen_circumference=profile_data.get('abdomen_circumference'),
                arm_circumference=profile_data.get('arm_circumference'),
                hip_circumference=profile_data.get('hip_circumference'),
                thigh_circumference=profile_data.get('thigh_circumference'),
                gym_access=profile_data.get('gym_access', False),
                workout_days_per_week=profile_data.get('workout_days_per_week', 3),
                preferred_workout_time=profile_data.get('preferred_workout_time'),
                preferred_intensity=profile_data.get('preferred_intensity'),
                # Trainer Professional Details
                certifications=profile_data.get('certifications'),
                qualifications=profile_data.get('qualifications'),
                years_of_experience=profile_data.get('years_of_experience'),
                specialization=profile_data.get('specialization'),
                education=profile_data.get('education'),
                bio=profile_data.get('bio')
            )
            
            # Set JSON fields
            if profile_data.get('fitness_goals'):
                profile.set_fitness_goals(profile_data['fitness_goals'])
            if profile_data.get('injuries'):
                profile.set_injuries(profile_data['injuries'])
            if profile_data.get('injury_details'):
                profile.injury_details = profile_data['injury_details']
            if profile_data.get('medical_conditions'):
                profile.set_medical_conditions(profile_data['medical_conditions'])
            if profile_data.get('medical_condition_details'):
                profile.medical_condition_details = profile_data['medical_condition_details']
            if profile_data.get('equipment_access'):
                profile.set_equipment_access(profile_data['equipment_access'])
            if profile_data.get('home_equipment'):
                profile.set_home_equipment(profile_data['home_equipment'])
            
            db.session.add(profile)
        
        db.session.commit()
        
        # Return password in response (only time it's available)
        return jsonify({
            'message': 'Assistant created successfully',
            'assistant': {
                'id': assistant.id,
                'username': assistant.username,
                'email': assistant.email,
                'password': password,  # Return password so admin can see it
                'profile_complete': profile_data != {}
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/assistants/<int:assistant_id>', methods=['DELETE'])
@jwt_required()
def delete_assistant(assistant_id):
    """Delete an assistant (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    User = get_user_model()
    UserProfile = get_userprofile_model()
    
    assistant = db.session.query(User).filter_by(id=assistant_id, role='assistant').first()
    if not assistant:
        return jsonify({'error': 'Assistant not found'}), 404
    
    # Check if assistant has assigned members
    assigned_members_count = db.session.query(User).filter_by(assigned_to=assistant_id).count()
    if assigned_members_count > 0:
        return jsonify({
            'error': f'Cannot delete assistant with {assigned_members_count} assigned members. Please reassign members first.'
        }), 400
    
    try:
        # Delete profile first
        profile = db.session.query(UserProfile).filter_by(user_id=assistant_id).first()
        if profile:
            db.session.delete(profile)
        
        # Delete user
        db.session.delete(assistant)
        db.session.commit()
        
        return jsonify({'message': 'Assistant deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ==================== Member Management ====================

@admin_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members():
    """Get all members (admin and assistants can see their assigned members)"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    User = get_user_model()
    user = db.session.get(User, int(user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role == 'admin':
        # Admin sees all members
        members = db.session.query(User).filter_by(role='member').all()
    elif user.role == 'assistant':
        # Assistant sees only assigned members
        members = db.session.query(User).filter_by(role='member', assigned_to=user_id).all()
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    members_data = []
    for member in members:
        profile = db.session.query(UserProfile).filter_by(user_id=member.id).first()
        assigned_to_user = None
        if member.assigned_to:
            assigned_to = db.session.get(User, member.assigned_to)
            assigned_to_user = {
                'id': assigned_to.id,
                'username': assigned_to.username,
                'role': assigned_to.role
            } if assigned_to else None
        
        members_data.append({
            'id': member.id,
            'username': member.username,
            'email': member.email,
            'assigned_to': assigned_to_user,
            'profile': {
                'age': profile.age if profile else None,
                'weight': profile.weight if profile else None,
                'height': profile.height if profile else None,
                'gender': profile.gender if profile else None,
                'training_level': profile.training_level if profile else None,
                'account_type': profile.account_type if profile else None
            } if profile else None
        })
    
    return jsonify(members_data), 200

@admin_bp.route('/members/<int:member_id>/assign', methods=['POST'])
@jwt_required()
def assign_member(member_id):
    """Assign a member to an assistant or admin (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    assigned_to_id = data.get('assigned_to_id')  # Assistant or admin ID
    
    User = get_user_model()
    member = db.session.query(User).filter_by(id=member_id, role='member').first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    if assigned_to_id:
        assigned_to = db.session.get(User, assigned_to_id)
        if not assigned_to or assigned_to.role not in ['admin', 'assistant']:
            return jsonify({'error': 'Invalid assistant/admin ID'}), 400
        member.assigned_to = assigned_to_id
    else:
        # Unassign
        member.assigned_to = None
    
    try:
        db.session.commit()
        return jsonify({'message': 'Member assignment updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/members/<int:member_id>/profile', methods=['PUT'])
@jwt_required()
def update_member_profile(member_id):
    """Update member profile details (admin only)"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    User = get_user_model()
    member = db.session.query(User).filter_by(id=member_id, role='member').first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    data = request.get_json()
    profile = db.session.query(UserProfile).filter_by(user_id=member_id).first()
    
    if not profile:
        # Create profile if doesn't exist
        profile = UserProfile(user_id=member_id, account_type='member')
        db.session.add(profile)
    
    # Update all profile fields
    for key, value in data.items():
        if hasattr(profile, key):
            if key in ['fitness_goals', 'injuries', 'medical_conditions', 'equipment_access', 'home_equipment']:
                # Handle JSON fields
                if hasattr(profile, f'set_{key}'):
                    getattr(profile, f'set_{key}')(value)
                else:
                    setattr(profile, key, json.dumps(value) if isinstance(value, list) else value)
            else:
                setattr(profile, key, value)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Member profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_member(member_id):
    """Delete a member (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    User = get_user_model()
    UserProfile = get_userprofile_model()
    
    member = db.session.query(User).filter_by(id=member_id, role='member').first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    try:
        # Delete profile first
        profile = db.session.query(UserProfile).filter_by(user_id=member_id).first()
        if profile:
            db.session.delete(profile)
        
        # Delete user
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': 'Member deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/members/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member_details(member_id):
    """Get detailed member information (admin and assistants can see their assigned members)"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    User = get_user_model()
    user = db.session.get(User, int(user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    member = db.session.query(User).filter_by(id=member_id, role='member').first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    # Check if user has permission to view this member
    if user.role == 'admin':
        # Admin can see all members
        pass
    elif user.role == 'assistant':
        # Assistant can only see assigned members
        if member.assigned_to != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    profile = db.session.query(UserProfile).filter_by(user_id=member_id).first()
    
    member_data = {
        'id': member.id,
        'username': member.username,
        'email': member.email,
        'created_at': member.created_at.isoformat() if member.created_at else None,
        'profile': None
    }
    
    if profile:
        member_data['profile'] = {
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
            'gender': profile.gender,
            'training_level': profile.training_level,
            'account_type': profile.account_type,
            'chest_circumference': profile.chest_circumference,
            'waist_circumference': profile.waist_circumference,
            'abdomen_circumference': profile.abdomen_circumference,
            'arm_circumference': profile.arm_circumference,
            'hip_circumference': profile.hip_circumference,
            'thigh_circumference': profile.thigh_circumference,
            'fitness_goals': profile.get_fitness_goals(),
            'injuries': profile.get_injuries(),
            'injury_details': profile.injury_details,
            'medical_conditions': profile.get_medical_conditions(),
            'medical_condition_details': profile.medical_condition_details,
            'exercise_history_years': profile.exercise_history_years,
            'exercise_history_description': profile.exercise_history_description,
            'equipment_access': profile.get_equipment_access(),
            'gym_access': profile.gym_access,
            'home_equipment': profile.get_home_equipment(),
            'preferred_workout_time': profile.preferred_workout_time,
            'workout_days_per_week': profile.workout_days_per_week,
            'preferred_intensity': profile.preferred_intensity
        }
    
    return jsonify(member_data), 200

# ==================== Configuration Management ====================

@admin_bp.route('/config', methods=['GET'])
@jwt_required()
def get_configuration():
    """Get training levels and injuries configuration (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Try to get from database, if not exists return defaults
    from models import Configuration
    config = db.session.query(Configuration).first()
    
    if config:
        return jsonify({
            'training_levels': json.loads(config.training_levels) if config.training_levels else {},
            'injuries': json.loads(config.injuries) if config.injuries else {}
        }), 200
    else:
        # Return empty defaults
        return jsonify({
            'training_levels': {
                'beginner': {'description_fa': '', 'description_en': ''},
                'intermediate': {'description_fa': '', 'description_en': ''},
                'advanced': {'description_fa': '', 'description_en': ''}
            },
            'injuries': {
                'knee': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''},
                'shoulder': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''},
                'lower_back': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''},
                'neck': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''},
                'wrist': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''},
                'ankle': {'description_fa': '', 'description_en': '', 'prevention_fa': '', 'prevention_en': ''}
            }
        }), 200

@admin_bp.route('/config', methods=['POST'])
@jwt_required()
def save_configuration():
    """Save training levels and injuries configuration (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    training_levels = data.get('training_levels', {})
    injuries = data.get('injuries', {})
    
    from models import Configuration
    config = db.session.query(Configuration).first()
    
    if not config:
        config = Configuration()
        db.session.add(config)
    
    config.training_levels = json.dumps(training_levels, ensure_ascii=False)
    config.injuries = json.dumps(injuries, ensure_ascii=False)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Configuration saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/check-profile-complete', methods=['GET'])
@jwt_required()
def check_profile_complete():
    """Check if current user (assistant) has completed their profile"""
    db = get_db()
    UserProfile = get_userprofile_model()
    user_id = get_jwt_identity()
    
    User = get_user_model()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'assistant':
        return jsonify({'profile_complete': True, 'message': 'Not an assistant'}), 200
    
    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    
    if not profile or profile.account_type != 'assistant':
        return jsonify({'profile_complete': False, 'message': 'Profile not complete'}), 200
    
    # Check if essential fields are filled
    profile_complete = bool(
        profile.age and
        profile.weight and
        profile.height and
        profile.gender and
        profile.training_level
    )
    
    return jsonify({
        'profile_complete': profile_complete,
        'message': 'Profile complete' if profile_complete else 'Profile incomplete'
    }), 200



