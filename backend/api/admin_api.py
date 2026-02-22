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
    db = get_db()
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
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
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
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
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
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
        return jsonify({'message': 'Exercise deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/exercises/<int:exercise_id>/movement-info', methods=['PATCH'])
@jwt_required()
def update_exercise_movement_info(exercise_id):
    """Update only video/voice/trainer notes for an exercise (training movement info)."""
    db = get_db()
    Exercise = get_exercise_model()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    exercise = db.session.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    data = request.get_json() or {}
    for key in ('video_url', 'voice_url', 'trainer_notes_fa', 'trainer_notes_en', 'note_notify_at_seconds', 'ask_post_set_questions'):
        if key in data and hasattr(exercise, key):
            val = data[key]
            if key == 'note_notify_at_seconds':
                try:
                    setattr(exercise, key, int(val) if val is not None and str(val).strip() != '' else None)
                except (TypeError, ValueError):
                    setattr(exercise, key, None)
            elif key == 'ask_post_set_questions':
                setattr(exercise, key, bool(val))
            else:
                setattr(exercise, key, (val.strip() if isinstance(val, str) else val) or None)
    try:
        db.session.commit()
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
        return jsonify(exercise.to_dict('fa')), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/exercises/video-upload', methods=['POST'])
@jwt_required()
def upload_exercise_video():
    """Upload a video file for an exercise; returns { video_url: ... }."""
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from werkzeug.utils import secure_filename
    import os
    from datetime import datetime
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    ext = (file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else '') or 'mp4'
    if ext not in ('mp4', 'webm', 'mov', 'avi', 'mkv'):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, webm, mov, avi, mkv'}), 400
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'exercises', 'videos')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(f"video_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    video_url = f'/api/uploads/exercises/videos/{filename}'
    return jsonify({'video_url': video_url, 'filename': filename}), 200


@admin_bp.route('/exercises/<int:exercise_id>/propagate-notes', methods=['POST'])
@jwt_required()
def propagate_exercise_notes(exercise_id):
    """Copy this exercise's trainer notes (and voice) to all programs that contain this movement.
    Sets TrainingActionNote for every (program_id, session_index, exercise_index) where the
    exercise name matches. Voice/text is set once on the movement and added to members' training program."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import TrainingProgram, TrainingActionNote
    Exercise = get_exercise_model()
    exercise = db.session.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    name_fa = (exercise.name_fa or '').strip()
    name_en = (exercise.name_en or '').strip()
    note_fa = exercise.trainer_notes_fa or ''
    note_en = exercise.trainer_notes_en or ''
    voice_url = exercise.voice_url or ''
    if not name_fa and not name_en:
        return jsonify({'error': 'Exercise has no name'}), 400
    programs = db.session.query(TrainingProgram).all()
    updated = 0
    for program in programs:
        sessions_list = program.get_sessions() if hasattr(program, 'get_sessions') else []
        for session_idx, session in enumerate(sessions_list):
            exercises_list = session.get('exercises') or []
            for ex_idx, ex in enumerate(exercises_list):
                ex_name_fa = (ex.get('name_fa') or ex.get('name') or '').strip()
                ex_name_en = (ex.get('name_en') or ex.get('name') or '').strip()
                if (name_fa and ex_name_fa == name_fa) or (name_en and ex_name_en == name_en):
                    existing = db.session.query(TrainingActionNote).filter_by(
                        training_program_id=program.id,
                        session_index=session_idx,
                        exercise_index=ex_idx,
                    ).first()
                    if existing:
                        existing.note_fa = note_fa or None
                        existing.note_en = note_en or None
                        existing.voice_url = voice_url or None
                    else:
                        row = TrainingActionNote(
                            training_program_id=program.id,
                            session_index=session_idx,
                            exercise_index=ex_idx,
                            note_fa=note_fa or None,
                            note_en=note_en or None,
                            voice_url=voice_url or None,
                            created_by=int(user_id) if user_id else None,
                        )
                        db.session.add(row)
                    updated += 1
    try:
        db.session.commit()
        return jsonify({'message': 'Notes propagated to programs', 'updated_count': updated}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/exercises/voice-upload', methods=['POST'])
@jwt_required()
def upload_exercise_voice():
    """Upload a voice note for an exercise; returns { voice_url: ... }."""
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from werkzeug.utils import secure_filename
    import os
    from datetime import datetime
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    ext = (file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else '') or 'webm'
    if ext not in ('webm', 'mp3', 'ogg', 'wav', 'm4a'):
        return jsonify({'error': 'Invalid file type. Allowed: webm, mp3, ogg, wav, m4a'}), 400
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'exercises', 'voice')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(f"voice_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    voice_url = f'/api/uploads/exercises/voice/{filename}'
    return jsonify({'voice_url': voice_url, 'filename': filename}), 200


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
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
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

@admin_bp.route('/assistants/<int:assistant_id>', methods=['GET'])
@jwt_required()
def get_assistant(assistant_id):
    """Get single assistant with full profile (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    User = get_user_model()
    UserProfile = get_userprofile_model()
    assistant = db.session.query(User).filter_by(id=assistant_id, role='assistant').first()
    if not assistant:
        return jsonify({'error': 'Assistant not found'}), 404
    profile = db.session.query(UserProfile).filter_by(user_id=assistant_id).first()
    out = {
        'id': assistant.id,
        'username': assistant.username,
        'email': assistant.email,
        'language': getattr(assistant, 'language', 'fa') or 'fa',
        'profile': None
    }
    if profile:
        out['profile'] = {
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
            'gender': profile.gender or '',
            'training_level': profile.training_level or '',
            'chest_circumference': profile.chest_circumference,
            'waist_circumference': profile.waist_circumference,
            'abdomen_circumference': profile.abdomen_circumference,
            'arm_circumference': profile.arm_circumference,
            'hip_circumference': profile.hip_circumference,
            'thigh_circumference': profile.thigh_circumference,
            'fitness_goals': profile.get_fitness_goals(),
            'injuries': profile.get_injuries(),
            'injury_details': profile.injury_details or '',
            'medical_conditions': profile.get_medical_conditions(),
            'medical_condition_details': profile.medical_condition_details or '',
            'exercise_history_years': profile.exercise_history_years,
            'exercise_history_description': profile.exercise_history_description or '',
            'equipment_access': profile.get_equipment_access(),
            'gym_access': profile.gym_access or False,
            'home_equipment': profile.get_home_equipment(),
            'preferred_workout_time': profile.preferred_workout_time or '',
            'workout_days_per_week': profile.workout_days_per_week,
            'preferred_intensity': profile.preferred_intensity or '',
            'certifications': profile.certifications or '',
            'qualifications': profile.qualifications or '',
            'years_of_experience': profile.years_of_experience,
            'specialization': profile.specialization or '',
            'education': profile.education or '',
            'bio': profile.bio or ''
        }
    return jsonify(out), 200

@admin_bp.route('/assistants/<int:assistant_id>', methods=['PUT'])
@jwt_required()
def update_assistant(assistant_id):
    """Update assistant account and profile (admin only)"""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    User = get_user_model()
    UserProfile = get_userprofile_model()
    assistant = db.session.query(User).filter_by(id=assistant_id, role='assistant').first()
    if not assistant:
        return jsonify({'error': 'Assistant not found'}), 404
    data = request.get_json() or {}
    if 'username' in data and data['username']:
        existing = db.session.query(User).filter(User.username == data['username'], User.id != assistant_id).first()
        if existing:
            return jsonify({'error': 'Username already taken'}), 400
        assistant.username = data['username']
    if 'email' in data and data['email']:
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        existing = db.session.query(User).filter(User.email == data['email'], User.id != assistant_id).first()
        if existing:
            return jsonify({'error': 'Email already taken'}), 400
        assistant.email = data['email']
    if 'language' in data:
        assistant.language = data['language'] or 'fa'
    if 'password' in data and data.get('password'):
        assistant.password_hash = generate_password_hash(data['password'])
    profile_data = data.get('profile', {})
    if profile_data is not None:
        profile = db.session.query(UserProfile).filter_by(user_id=assistant_id).first()
        if not profile:
            profile = UserProfile(user_id=assistant_id, account_type='assistant')
            db.session.add(profile)
        for key, value in profile_data.items():
            if hasattr(profile, key):
                if key in ['fitness_goals', 'injuries', 'medical_conditions', 'equipment_access', 'home_equipment']:
                    if hasattr(profile, f'set_{key}'):
                        getattr(profile, f'set_{key}')(value)
                    else:
                        setattr(profile, key, json.dumps(value) if isinstance(value, list) else value)
                else:
                    setattr(profile, key, value)
    try:
        db.session.commit()
        return jsonify({'message': 'Assistant updated successfully'}), 200
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

@admin_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    """Update member account info (username, email) - admin only"""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    User = get_user_model()
    member = db.session.query(User).filter_by(id=member_id, role='member').first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    data = request.get_json() or {}
    if 'username' in data and data['username']:
        existing = db.session.query(User).filter(User.username == data['username'], User.id != member_id).first()
        if existing:
            return jsonify({'error': 'Username already taken'}), 400
        member.username = data['username']
    if 'email' in data and data['email']:
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        existing = db.session.query(User).filter(User.email == data['email'], User.id != member_id).first()
        if existing:
            return jsonify({'error': 'Email already taken'}), 400
        member.email = data['email']
    if 'language' in data:
        member.language = data['language'] or 'fa'
    try:
        db.session.commit()
        return jsonify({
            'message': 'Member updated successfully',
            'username': member.username,
            'email': member.email
        }), 200
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
    
    def _default_purposes():
        return {
            'lose_weight': {'sessions_per_week': '', 'sets_per_action': '', 'reps_per_action': '', 'training_focus_fa': '', 'training_focus_en': '', 'break_between_sets': ''},
            'gain_weight': {'sessions_per_week': '', 'sets_per_action': '', 'reps_per_action': '', 'training_focus_fa': '', 'training_focus_en': '', 'break_between_sets': ''},
            'gain_muscle': {'sessions_per_week': '', 'sets_per_action': '', 'reps_per_action': '', 'training_focus_fa': '', 'training_focus_en': '', 'break_between_sets': ''},
            'shape_fitting': {'sessions_per_week': '', 'sets_per_action': '', 'reps_per_action': '', 'training_focus_fa': '', 'training_focus_en': '', 'break_between_sets': ''}
        }

    def _default_level():
        return {'description_fa': '', 'description_en': '', 'goals': [], 'purposes': _default_purposes()}

    default_training_levels = {
        'beginner': _default_level(),
        'intermediate': _default_level(),
        'advanced': _default_level()
    }

    if config:
        raw_levels = json.loads(config.training_levels) if config.training_levels else {}
        training_levels_out = {}
        for level_key in ('beginner', 'intermediate', 'advanced'):
            stored = raw_levels.get(level_key) or {}
            merged = {
                'description_fa': stored.get('description_fa', ''),
                'description_en': stored.get('description_en', ''),
                'goals': stored.get('goals') if isinstance(stored.get('goals'), list) else [],
                'purposes': {}
            }
            default_p = _default_purposes()
            for purpose_key, default_purpose in default_p.items():
                stored_p = (stored.get('purposes') or {}).get(purpose_key) or {}
                merged['purposes'][purpose_key] = {**default_purpose, **stored_p}
            training_levels_out[level_key] = merged
        raw_injuries = json.loads(config.injuries) if config.injuries else {}
        injury_keys = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle']
        injuries_out = {}
        for key in injury_keys:
            stored = raw_injuries.get(key) or {}
            merged = {
                'purposes_fa': stored.get('purposes_fa', '') or stored.get('description_fa', ''),
                'purposes_en': stored.get('purposes_en', '') or stored.get('description_en', ''),
                'allowed_movements': stored.get('allowed_movements') if isinstance(stored.get('allowed_movements'), list) else [],
                'forbidden_movements': stored.get('forbidden_movements') if isinstance(stored.get('forbidden_movements'), list) else [],
                'important_notes_fa': stored.get('important_notes_fa', ''),
                'important_notes_en': stored.get('important_notes_en', '')
            }
            injuries_out[key] = merged
        injuries_out['common_injury_note_fa'] = raw_injuries.get('common_injury_note_fa', '')
        injuries_out['common_injury_note_en'] = raw_injuries.get('common_injury_note_en', '')
        return jsonify({
            'training_levels': training_levels_out,
            'injuries': injuries_out
        }), 200
    else:
        _default_injury = lambda: {
            'purposes_fa': '', 'purposes_en': '', 'allowed_movements': [], 'forbidden_movements': [],
            'important_notes_fa': '', 'important_notes_en': ''
        }
        default_injuries = {k: _default_injury() for k in ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle']}
        default_injuries['common_injury_note_fa'] = ''
        default_injuries['common_injury_note_en'] = ''
        return jsonify({
            'training_levels': default_training_levels,
            'injuries': default_injuries
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
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
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


# ==================== Break Requests (admin/assistant) ====================

@admin_bp.route('/break-requests', methods=['GET'])
@jwt_required()
def list_break_requests():
    """List break requests: admin sees all, assistant sees only from their assigned members."""
    db = get_db()
    User = get_user_model()
    user_id = get_jwt_identity()
    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    user = db.session.get(User, user_id_int)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.role not in ('admin', 'assistant'):
        return jsonify({'error': 'Unauthorized'}), 403

    from models import BreakRequest
    if user.role == 'admin':
        query = db.session.query(BreakRequest).order_by(BreakRequest.created_at.desc())
    else:
        member_ids = [m.id for m in db.session.query(User).filter_by(role='member', assigned_to=user_id_int).all()]
        if not member_ids:
            return jsonify([]), 200
        query = db.session.query(BreakRequest).filter(
            BreakRequest.user_id.in_(member_ids)
        ).order_by(BreakRequest.created_at.desc())

    status_filter = request.args.get('status')
    if status_filter in ('pending', 'seen', 'accepted', 'denied'):
        query = query.filter_by(status=status_filter)

    requests_list = query.limit(100).all()
    out = []
    for br in requests_list:
        member = db.session.get(User, br.user_id)
        out.append({
            'id': br.id,
            'user_id': br.user_id,
            'username': member.username if member else None,
            'message': br.message,
            'status': br.status,
            'created_at': br.created_at.isoformat() if br.created_at else None,
            'seen_at': br.seen_at.isoformat() if br.seen_at else None,
            'responded_at': br.responded_at.isoformat() if br.responded_at else None,
            'response_message': br.response_message,
        })
    return jsonify(out), 200


@admin_bp.route('/break-requests/<int:request_id>/seen', methods=['PATCH'])
@jwt_required()
def mark_break_request_seen(request_id):
    """Mark a break request as seen (admin or assistant who can see it)."""
    db = get_db()
    User = get_user_model()
    user_id = get_jwt_identity()
    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    user = db.session.get(User, user_id_int)
    if not user or user.role not in ('admin', 'assistant'):
        return jsonify({'error': 'Unauthorized'}), 403

    from models import BreakRequest
    br = db.session.query(BreakRequest).filter_by(id=request_id).first()
    if not br:
        return jsonify({'error': 'Break request not found'}), 404
    if user.role == 'assistant':
        member = db.session.get(User, br.user_id)
        if not member or member.assigned_to != user_id_int:
            return jsonify({'error': 'Unauthorized'}), 403

    from datetime import datetime
    br.status = 'seen'
    br.seen_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({
            'id': br.id,
            'status': br.status,
            'seen_at': br.seen_at.isoformat() if br.seen_at else None,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/break-requests/<int:request_id>/respond', methods=['PATCH'])
@jwt_required()
def respond_break_request(request_id):
    """Accept or deny a break request (admin or assistant who can see it)."""
    db = get_db()
    User = get_user_model()
    user_id = get_jwt_identity()
    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
    user = db.session.get(User, user_id_int)
    if not user or user.role not in ('admin', 'assistant'):
        return jsonify({'error': 'Unauthorized'}), 403

    from models import BreakRequest
    from datetime import datetime

    br = db.session.query(BreakRequest).filter_by(id=request_id).first()
    if not br:
        return jsonify({'error': 'Break request not found'}), 404
    if user.role == 'assistant':
        member = db.session.get(User, br.user_id)
        if not member or member.assigned_to != user_id_int:
            return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    action = (data.get('action') or '').strip().lower()
    if action not in ('accept', 'deny'):
        return jsonify({'error': 'action must be "accept" or "deny"'}), 400

    response_message = (data.get('message') or data.get('response_message') or '').strip() or None

    br.status = 'accepted' if action == 'accept' else 'denied'
    br.responded_at = datetime.utcnow()
    br.response_message = response_message
    if not br.seen_at:
        br.seen_at = br.responded_at

    try:
        db.session.commit()
        return jsonify({
            'id': br.id,
            'status': br.status,
            'responded_at': br.responded_at.isoformat() if br.responded_at else None,
            'response_message': br.response_message,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Site Settings (website info) ====================

@admin_bp.route('/site-settings', methods=['GET'])
@jwt_required()
def get_site_settings():
    """Get site settings (admin only)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import SiteSettings
    row = db.session.query(SiteSettings).first()
    if not row:
        return jsonify({
            'contact_email': '', 'contact_phone': '', 'address_fa': '', 'address_en': '',
            'app_description_fa': '', 'app_description_en': '',
            'instagram_url': '', 'telegram_url': '', 'whatsapp_url': '', 'twitter_url': '',
            'facebook_url': '', 'linkedin_url': '', 'youtube_url': '', 'copyright_text': '',
            'session_phases_json': '', 'training_plans_products_json': ''
        }), 200
    out = {
        'contact_email': row.contact_email or '',
        'contact_phone': row.contact_phone or '',
        'address_fa': row.address_fa or '', 'address_en': row.address_en or '',
        'app_description_fa': row.app_description_fa or '', 'app_description_en': row.app_description_en or '',
        'instagram_url': row.instagram_url or '', 'telegram_url': row.telegram_url or '',
        'whatsapp_url': row.whatsapp_url or '', 'twitter_url': row.twitter_url or '',
        'facebook_url': row.facebook_url or '', 'linkedin_url': row.linkedin_url or '',
        'youtube_url': row.youtube_url or '', 'copyright_text': row.copyright_text or '',
        'session_phases_json': row.session_phases_json if hasattr(row, 'session_phases_json') and row.session_phases_json else '',
        'training_plans_products_json': row.training_plans_products_json if hasattr(row, 'training_plans_products_json') and row.training_plans_products_json else '',
    }
    return jsonify(out), 200


@admin_bp.route('/site-settings', methods=['PUT'])
@jwt_required()
def update_site_settings():
    """Update site settings (admin only)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() or {}
    from models import SiteSettings
    row = db.session.query(SiteSettings).first()
    if not row:
        row = SiteSettings()
        db.session.add(row)
    for key in ('contact_email', 'contact_phone', 'address_fa', 'address_en',
                'app_description_fa', 'app_description_en',
                'instagram_url', 'telegram_url', 'whatsapp_url', 'twitter_url',
                'facebook_url', 'linkedin_url', 'youtube_url', 'copyright_text'):
        if key in data and data[key] is not None and hasattr(row, key):
            val = data[key]
            setattr(row, key, (val.strip() if isinstance(val, str) else val))
    for key in ('session_phases_json', 'training_plans_products_json'):
        if key in data and hasattr(row, key):
            val = data[key]
            if val is None:
                setattr(row, key, None)
            elif isinstance(val, str):
                setattr(row, key, val.strip() or None)
            elif isinstance(val, (dict, list)):
                setattr(row, key, json.dumps(val, ensure_ascii=False))
            else:
                setattr(row, key, str(val))
    try:
        db.session.commit()
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
        return jsonify({'message': 'Site settings saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ---------- Session phases (warming, cooldown, ending) for member session steps ----------
@admin_bp.route('/session-phases', methods=['GET'])
@jwt_required()
def get_session_phases():
    """Get warming, cooldown, ending message (admin)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
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
    try:
        return jsonify(json.loads(raw)), 200
    except Exception:
        return jsonify({
            'warming': {'title_fa': '', 'title_en': '', 'steps': []},
            'cooldown': {'title_fa': '', 'title_en': '', 'steps': []},
            'ending_message_fa': '',
            'ending_message_en': ''
        }), 200


@admin_bp.route('/session-phases', methods=['PUT'])
@jwt_required()
def update_session_phases():
    """Update warming, cooldown, ending message (admin)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid body'}), 400
    from models import SiteSettings
    row = db.session.query(SiteSettings).first()
    if not row:
        row = SiteSettings()
        db.session.add(row)
    row.session_phases_json = json.dumps(data, ensure_ascii=False)
    try:
        db.session.commit()
        try:
            from services.website_kb import trigger_kb_reindex_async
            trigger_kb_reindex_async()
        except Exception:
            pass
        return jsonify({'message': 'Session phases saved'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ---------- Training plans & packages (buy modal content) ----------
@admin_bp.route('/training-plans-products', methods=['GET'])
@jwt_required()
def get_training_plans_products():
    """Get buyable training plans and packages config (admin)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    from models import SiteSettings
    row = db.session.query(SiteSettings).first()
    raw = (getattr(row, 'training_plans_products_json', None) or '').strip() if row else ''
    if not raw:
        return jsonify({'basePrograms': [], 'packages': []}), 200
    try:
        return jsonify(json.loads(raw)), 200
    except Exception:
        return jsonify({'basePrograms': [], 'packages': []}), 200


@admin_bp.route('/training-plans-products', methods=['PUT'])
@jwt_required()
def update_training_plans_products():
    """Update buyable training plans and packages (admin)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid body'}), 400
    db = get_db()
    from models import SiteSettings
    row = db.session.query(SiteSettings).first()
    if not row:
        row = SiteSettings()
        db.session.add(row)
    row.training_plans_products_json = json.dumps(data, ensure_ascii=False)
    try:
        db.session.commit()
        try:
            from services.website_kb import trigger_kb_reindex_safe
            trigger_kb_reindex_safe()
        except Exception:
            pass
        return jsonify({'message': 'Training plans & packages saved'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ---------- AI Settings (provider keys + selected provider) ----------
@admin_bp.route('/ai-settings', methods=['GET'])
@jwt_required()
def get_ai_settings():
    """Get AI provider settings (no API keys in response). Admin only."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        from services.ai_provider import _get_settings, get_provider_api_key, is_sdk_installed, PROVIDERS, SELECTED_DEFAULT
        settings = _get_settings()
        selected = settings.get('selected_provider') or SELECTED_DEFAULT
        providers = {}
        for p in PROVIDERS:
            key, source = get_provider_api_key(p, settings)
            prov_data = settings.get(p) or {}
            providers[p] = {
                'sdk_installed': is_sdk_installed(p),
                'has_key': bool(key),
                'source': source or (None if not key else 'database'),
                'is_valid': prov_data.get('is_valid', False),
                'last_tested_at': prov_data.get('last_tested_at'),
            }
        return jsonify({
            'selected_provider': selected,
            'providers': providers,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/ai-settings', methods=['PUT'])
@jwt_required()
def update_ai_settings():
    """Update AI settings: selected_provider and/or API keys per provider. Admin only."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid body'}), 400
    try:
        from services.ai_provider import _get_settings, _save_settings, PROVIDERS, SELECTED_DEFAULT
        settings = _get_settings()
        selectable = ('auto',) + PROVIDERS
        if 'selected_provider' in data and data['selected_provider'] in selectable:
            settings['selected_provider'] = data['selected_provider']
        for p in PROVIDERS:
            if p in data and isinstance(data[p], dict) and 'api_key' in data[p]:
                key = data[p]['api_key']
                if p not in settings:
                    settings[p] = {}
                if key is None or (isinstance(key, str) and not key.strip()):
                    settings[p].pop('api_key', None)
                else:
                    settings[p]['api_key'] = key.strip() if isinstance(key, str) else str(key)
        if not _save_settings(settings):
            return jsonify({'error': 'Failed to save settings'}), 500
        return jsonify({'message': 'AI settings saved'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- Website KB ----------
@admin_bp.route('/website-kb/status', methods=['GET'])
@jwt_required()
def kb_status():
    if not is_admin(get_jwt_identity()):
        return jsonify({'error': 'Unauthorized'}), 403
    from services.website_kb import get_kb_status
    status = get_kb_status()
    return jsonify({
        'updated_at': status.get('updated_at'),
        'count': status.get('count', 0),
    }), 200


@admin_bp.route('/website-kb/reindex', methods=['POST'])
@jwt_required()
def kb_reindex():
    if not is_admin(get_jwt_identity()):
        return jsonify({'error': 'Unauthorized'}), 403
    from services.website_kb import build_kb_index
    try:
        payload = build_kb_index()
        return jsonify({
            'message': 'KB reindexed',
            'count': payload.get('count', 0),
            'updated_at': payload.get('updated_at'),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/ai-settings/test', methods=['POST'])
@jwt_required()
def test_ai_provider():
    """Test an AI provider's API key. Body: { provider: 'openai'|'anthropic'|'gemini', api_key?: optional }. Admin only."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() or {}
    provider = (data.get('provider') or '').strip().lower()
    if provider not in ('openai', 'anthropic', 'gemini', 'vertex'):
        return jsonify({'error': 'Invalid provider'}), 400
    api_key_override = data.get('api_key')
    if api_key_override is not None and isinstance(api_key_override, str):
        api_key_override = api_key_override.strip() or None
    try:
        from services.ai_provider import test_provider
        success, message = test_provider(provider, api_key_override)
        return jsonify({'success': success, 'message': message}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 200


# ---------- Progress check requests (trainer accept/deny) ----------
@admin_bp.route('/progress-check-requests', methods=['GET'])
@jwt_required()
def list_progress_check_requests():
    """List pending progress check requests (admin/assistant)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import ProgressCheckRequest, User
    status_filter = request.args.get('status', 'pending')
    q = db.session.query(ProgressCheckRequest)
    if status_filter:
        q = q.filter_by(status=status_filter)
    q = q.order_by(ProgressCheckRequest.requested_at.desc()).limit(50)
    rows = q.all()
    out = []
    for r in rows:
        member = db.session.get(User, r.member_id)
        out.append({
            'id': r.id,
            'member_id': r.member_id,
            'member_username': member.username if member else None,
            'status': r.status,
            'requested_at': r.requested_at.isoformat() if r.requested_at else None,
            'responded_at': r.responded_at.isoformat() if r.responded_at else None,
        })
    return jsonify(out), 200


@admin_bp.route('/progress-check-requests/<int:req_id>', methods=['PATCH'])
@jwt_required()
def respond_progress_check_request(req_id):
    """Accept or deny a progress check request (admin/assistant)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import ProgressCheckRequest, Notification
    data = request.get_json() or {}
    action = (data.get('action') or '').strip().lower()
    if action not in ('accept', 'deny'):
        return jsonify({'error': 'action must be accept or deny'}), 400
    req = db.session.query(ProgressCheckRequest).filter_by(id=req_id).first()
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    if req.status != 'pending':
        return jsonify({'error': 'Request already responded'}), 400
    from datetime import datetime
    req.status = 'accepted' if action == 'accept' else 'denied'
    req.responded_at = datetime.utcnow()
    req.responded_by = user_id
    if action == 'accept':
        notif = Notification(
            user_id=req.member_id,
            type='message',
            title_fa='بررسی پیشرفت پذیرفته شد',
            title_en='Progress check accepted',
            body_fa='مربی درخواست بررسی پیشرفت شما را پذیرفت.',
            body_en='Your trainer has accepted your progress check request.'
        )
        db.session.add(notif)
    else:
        notif = Notification(
            user_id=req.member_id,
            type='message',
            title_fa='درخواست بررسی پیشرفت رد شد',
            title_en='Progress check request declined',
            body_fa='مربی در این زمان نتوانست درخواست بررسی پیشرفت شما را بپذیرد.',
            body_en='Your trainer could not fulfill your progress check request at this time.'
        )
        db.session.add(notif)
    try:
        db.session.commit()
        return jsonify({'id': req.id, 'status': req.status, 'message': 'Updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ---------- Admin list all training programs ----------
@admin_bp.route('/programs', methods=['GET'])
@jwt_required()
def list_programs():
    """List all training programs for admin/assistant (to manage action notes)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import TrainingProgram
    language = request.args.get('language', 'fa')
    programs = db.session.query(TrainingProgram).order_by(TrainingProgram.id).all()
    out = [p.to_dict(language) for p in programs]
    return jsonify(out), 200


# ---------- Admin cleanup: keep single training program ----------
@admin_bp.route('/training-programs/cleanup', methods=['POST'])
@jwt_required()
def cleanup_training_programs():
    """Keep one general program and one program per member. Body: { dry_run?: bool }."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    dry_run = bool(data.get('dry_run', False))

    from app import User
    from models import TrainingProgram, MemberWeeklyGoal, MemberTrainingActionCompletion, TrainingActionNote

    # General programs: keep the first by id
    general = (
        db.session.query(TrainingProgram)
        .filter(TrainingProgram.user_id.is_(None))
        .order_by(TrainingProgram.id)
        .all()
    )
    if not general:
        return jsonify({'error': 'No general training programs found'}), 400

    keep_general = general[0]
    extra_general = general[1:]
    removed_general = len(extra_general)

    if not dry_run and extra_general:
        for prog in extra_general:
            pid = prog.id
            db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
            db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
            db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
            db.session.delete(prog)

    # Member programs: keep first per member, assign if none
    members = db.session.query(User).filter(User.role == 'member').order_by(User.id).all()
    removed_member_programs = 0
    assigned = 0
    for member in members:
        programs = (
            db.session.query(TrainingProgram)
            .filter_by(user_id=member.id)
            .order_by(TrainingProgram.id)
            .all()
        )
        if programs:
            for prog in programs[1:]:
                pid = prog.id
                if not dry_run:
                    db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
                    db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
                    db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
                    db.session.delete(prog)
                removed_member_programs += 1
            continue

        # No program: copy the single general program
        if not dry_run:
            copy_program = TrainingProgram(
                user_id=member.id,
                name_fa=keep_general.name_fa,
                name_en=keep_general.name_en,
                description_fa=keep_general.description_fa,
                description_en=keep_general.description_en,
                duration_weeks=keep_general.duration_weeks,
                training_level=keep_general.training_level,
                category=keep_general.category,
                sessions=keep_general.sessions,
            )
            db.session.add(copy_program)
        assigned += 1

    if not dry_run:
        db.session.commit()

    return jsonify({
        'dry_run': dry_run,
        'kept_general_program_id': keep_general.id,
        'removed_general_programs': removed_general,
        'removed_member_programs': removed_member_programs,
        'assigned_to_members': assigned,
    }), 200


# ---------- Training action notes (admin: notes/voice per exercise) ----------
@admin_bp.route('/programs/<int:program_id>/action-notes', methods=['GET'])
@jwt_required()
def get_action_notes(program_id):
    """Get all trainer notes for a program (admin/assistant)."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import TrainingProgram, TrainingActionNote
    program = db.session.get(TrainingProgram, program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    rows = db.session.query(TrainingActionNote).filter_by(training_program_id=program_id).all()
    language = request.args.get('language', 'fa')
    out = []
    for r in rows:
        out.append({
            'session_index': r.session_index,
            'exercise_index': r.exercise_index,
            'note_fa': r.note_fa or '',
            'note_en': r.note_en or '',
            'note': r.note_fa if language == 'fa' else r.note_en,
            'voice_url': r.voice_url or '',
        })
    return jsonify(out), 200


@admin_bp.route('/programs/<int:program_id>/action-notes', methods=['PUT'])
@jwt_required()
def update_action_notes(program_id):
    """Bulk update trainer notes for a program. Body: { notes: [{ session_index, exercise_index, note_fa?, note_en?, voice_url? }], notify_members?: bool }."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from models import TrainingProgram, TrainingActionNote, Notification, MemberWeeklyGoal
    from app import User
    from datetime import datetime
    program = db.session.get(TrainingProgram, program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    data = request.get_json() or {}
    notes_list = data.get('notes') or []
    notify_members = data.get('notify_members', False)
    for item in notes_list:
        si = int(item.get('session_index', 0))
        ei = int(item.get('exercise_index', 0))
        note_fa = (item.get('note_fa') or '').strip()
        note_en = (item.get('note_en') or '').strip()
        voice_url = (item.get('voice_url') or '').strip()
        existing = db.session.query(TrainingActionNote).filter_by(
            training_program_id=program_id, session_index=si, exercise_index=ei
        ).first()
        if existing:
            existing.note_fa = note_fa or None
            existing.note_en = note_en or None
            existing.voice_url = voice_url or None
            existing.updated_at = datetime.utcnow()
        else:
            if note_fa or note_en or voice_url:
                row = TrainingActionNote(
                    training_program_id=program_id,
                    session_index=si,
                    exercise_index=ei,
                    note_fa=note_fa or None,
                    note_en=note_en or None,
                    voice_url=voice_url or None,
                    created_by=int(user_id) if user_id else None,
                )
                db.session.add(row)
    db.session.commit()
    if notify_members:
        member_ids = set()
        for g in db.session.query(MemberWeeklyGoal).filter_by(training_program_id=program_id).all():
            member_ids.add(g.user_id)
        if program.user_id:
            member_ids.add(program.user_id)
        title_fa = 'یادداشت جدید از مربی'
        title_en = 'New note from your trainer'
        body_fa = 'مربی شما یک یادداشت یا نکته برای تمرینات شما اضافه کرده است. در برنامه تمرینی مشاهده کنید.'
        body_en = 'Your trainer added a note or tip for your workout. Check your training program.'
        for uid in member_ids:
            n = Notification(
                user_id=uid,
                title_fa=title_fa,
                title_en=title_en,
                body_fa=body_fa,
                body_en=body_en,
                type='trainer_note',
                link='?tab=training-program',
            )
            db.session.add(n)
        db.session.commit()
    return jsonify({'message': 'Action notes saved', 'notify_members': notify_members}), 200


@admin_bp.route('/action-notes/voice-upload', methods=['POST'])
@jwt_required()
def upload_voice_note():
    """Upload a voice note file; returns { voice_url: ... } for use in action notes."""
    db = get_db()
    user_id = get_jwt_identity()
    if not is_admin_or_assistant(user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    from werkzeug.utils import secure_filename
    import os
    from datetime import datetime
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    ext = (file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else '') or 'webm'
    if ext not in ('webm', 'mp3', 'ogg', 'wav', 'm4a'):
        return jsonify({'error': 'Invalid file type. Allowed: webm, mp3, ogg, wav, m4a'}), 400
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'voice_notes')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(f"voice_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    voice_url = f'/api/uploads/voice_notes/{filename}'
    return jsonify({'voice_url': voice_url, 'filename': filename}), 200



