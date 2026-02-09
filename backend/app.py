from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
import base64
from dotenv import load_dotenv

load_dotenv()

# Import models to avoid circular imports - import after db is created
# We'll import specific classes as needed to avoid conflicts

# Import workout plan API
try:
    from api.workout_plan_api import workout_plan_bp
except ImportError:
    workout_plan_bp = None

FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
app = Flask(__name__, static_folder=FRONTEND_BUILD_DIR, static_url_path='')
# Database: PostgreSQL by default. Set DATABASE_URL in .env (see .env.example).
# Normalize postgres:// to postgresql:// (required by SQLAlchemy 1.4+ and many hosts like Heroku).
_db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/raha_fitness')
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
# If PostgreSQL is configured but not reachable, fall back to SQLite so the app can run
if _db_url.startswith('postgresql'):
    try:
        from sqlalchemy import create_engine
        _test = create_engine(_db_url, connect_args={"connect_timeout": 3})
        with _test.connect():
            pass
    except Exception:
        print("\n[INFO] PostgreSQL not reachable - using SQLite for this run. Start PostgreSQL and set DATABASE_URL for production.\n")
        _db_url = 'sqlite:///raha_fitness.db'
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Get JWT_SECRET_KEY from environment or use default
# IMPORTANT: This key must be consistent - if it changes, all existing tokens become invalid
jwt_secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Print JWT_SECRET_KEY on startup for debugging (first 20 chars only for security)
print(f"\n{'='*70}")
print(f"JWT Configuration:")
print(f"  JWT_SECRET_KEY: {jwt_secret_key[:20]}... (length: {len(jwt_secret_key)})")
print(f"  JWT_ACCESS_TOKEN_EXPIRES: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}")
print(f"  NOTE: If JWT_SECRET_KEY changes, all existing tokens become invalid")
print(f"{'='*70}\n")

# Print JWT_SECRET_KEY on startup for debugging (first 20 chars only for security)
print(f"\n{'='*60}")
print(f"JWT_SECRET_KEY configured: {jwt_secret_key[:20]}... (length: {len(jwt_secret_key)})")
print(f"{'='*60}\n")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads', 'profiles')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Import models module early to register all model classes
# This ensures relationships can resolve class names properly
# Note: models.py imports db from app, so we import after db is created
# We'll configure the User.nutrition_plans relationship after User class is defined
try:
    import models  # This registers NutritionPlan, Exercise, UserProfile, etc. in SQLAlchemy registry
except ImportError as e:
    print(f"Warning: Could not import models module: {e}. Some relationships may not work.")

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"JWT Token expired: {jwt_payload}")
    return jsonify({'error': 'Token has expired', 'message': 'Please log in again'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    """
    This callback is triggered when Flask-JWT-Extended cannot decode/validate a token.
    The error_string contains the exact reason why the token is invalid.
    """
    print(f"\n{'='*70}")
    print(f"JWT INVALID TOKEN - ROOT CAUSE")
    print(f"{'='*70}")
    print(f"Flask-JWT-Extended Error: {repr(error_string)}")
    print(f"Current JWT_SECRET_KEY (first 20 chars): {app.config['JWT_SECRET_KEY'][:20]}...")
    print(f"JWT_SECRET_KEY length: {len(app.config['JWT_SECRET_KEY'])}")
    
    # Log the Authorization header
    auth_header = request.headers.get('Authorization', '')
    print(f"\nAuthorization header length: {len(auth_header) if auth_header else 0}")
    
    if auth_header and auth_header.startswith('Bearer '):
        token_part = auth_header[7:]
        parts = token_part.split('.')
        print(f"Token structure: {len(parts)} parts (should be 3)")
        print(f"Token (first 50 chars): {token_part[:50]}...")
        
        # Most common causes:
        # 1. "Signature verification failed" = JWT_SECRET_KEY mismatch
        # 2. "Not enough segments" = Token format issue
        # 3. "Invalid header padding" = Token corruption
        if 'signature' in error_string.lower() or 'verification' in error_string.lower():
            print(f"\n{'='*70}")
            print(f"ROOT CAUSE: JWT_SECRET_KEY MISMATCH")
            print(f"The token signature cannot be verified with the current JWT_SECRET_KEY.")
            print(f"This means the token was created with a DIFFERENT secret key.")
            print(f"\nSOLUTION:")
            print(f"1. User must LOG OUT and LOG BACK IN to get a fresh token")
            print(f"2. Ensure JWT_SECRET_KEY is consistent (check .env file)")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print(f"ROOT CAUSE: {error_string}")
            print(f"{'='*70}\n")
    
    return jsonify({'error': 'Invalid token', 'message': 'Token format is invalid. Please log in again'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    print(f"JWT Missing token: {error_string}")
    return jsonify({'error': 'Authorization token is missing', 'message': 'Please log in'}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    print(f"JWT Token not fresh: {jwt_payload}")
    return jsonify({'error': 'Token is not fresh', 'message': 'Please log in again'}), 401

# Database Models
class User(db.Model):
    __tablename__ = 'user'  # Use singular to match existing database
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='fa')  # 'fa' for Farsi, 'en' for English
    role = db.Column(db.String(20), default='member')  # 'admin', 'assistant', 'member'
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # For members assigned to assistants/admins
    trial_ends_at = db.Column(db.DateTime, nullable=True)  # 7-day free trial end; null = no trial or not a member
    
    exercises = db.relationship('UserExercise', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    # Relationships for member assignments
    assigned_members = db.relationship('User', backref=db.backref('assigned_by', remote_side=[id]), lazy=True)
    # NutritionPlan relationship will be configured after models are imported


_admin_seeded = False


def ensure_default_admin():
    global _admin_seeded
    if _admin_seeded:
        return
    _admin_seeded = True

    try:
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        if not inspector.has_table('user'):
            print("[INFO] Skipping admin seed: user table not found.")
            return

        existing_admin = db.session.query(User).filter_by(role='admin').first()
        if existing_admin:
            return

        username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@insightgym.com')
        password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')

        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            language='fa',
            created_at=datetime.utcnow()
        )

        db.session.add(admin_user)
        db.session.commit()
        print(f"[INFO] Default admin created: username={username}, email={email}")
        if password == 'admin123' and not os.getenv('DEFAULT_ADMIN_PASSWORD'):
            print("[WARN] Using default admin password. Set DEFAULT_ADMIN_PASSWORD in production.")
    except Exception as exc:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f"[WARN] Admin seed failed: {exc}")


@app.before_request
def _ensure_admin_on_first_request():
    ensure_default_admin()

class UserExercise(db.Model):
    """User Exercise History - tracks user's completed exercises"""
    __tablename__ = 'user_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_name = db.Column(db.String(200), nullable=False)
    exercise_type = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # in minutes
    calories_burned = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(36), nullable=True, index=True)  # conversation/session grouping
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ChatSession(db.Model):
    """Optional custom title per conversation (session_id)."""
    __tablename__ = 'chat_session'
    session_id = db.Column(db.String(64), primary_key=True)  # uuid or _legacy_<id>
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrainerMessage(db.Model):
    """Member-to-trainer (admin/assistant) direct messages."""
    __tablename__ = 'trainer_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)


# NutritionPlan is defined in models.py to avoid duplicate class names

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    content_fa = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Configure User.nutrition_plans relationship after all models are defined
# This must be done after User class is defined and models module is imported
# Use a lambda to defer resolution until mapper configuration
# Note: User.nutrition_plans relationship is not configured here to avoid SQLAlchemy issues
# Nutrition plans can be accessed via direct queries: NutritionPlan.query.filter_by(user_id=user.id)
# This avoids the foreign key relationship issues between different modules

class Injury(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_fa = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    prevention_fa = db.Column(db.Text)
    prevention_en = db.Column(db.Text)
    treatment_fa = db.Column(db.Text)
    treatment_en = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    language = data.get('language', 'fa')
    
    # Profile data (optional during registration, can be completed later)
    profile_data = data.get('profile', {})
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Only members can signup - admin and assistants are created by admin
        # Force role to 'member' regardless of account_type in registration
        role = 'member'
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            language=language,
            role=role,
            trial_ends_at=datetime.utcnow() + timedelta(days=7),  # 7-day free trial for new members
        )
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create user profile if data provided
        if profile_data:
            try:
                from models import UserProfile
                import json
                
                print(f"Creating profile for user {user.id} with data: {profile_data}")
                
                profile = UserProfile(
                    user_id=user.id,
                    age=profile_data.get('age'),
                    weight=profile_data.get('weight'),
                    height=profile_data.get('height'),
                    gender=profile_data.get('gender'),
                    account_type=profile_data.get('account_type'),
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
                    preferred_intensity=profile_data.get('preferred_intensity')
                )
                
                # Set JSON fields
                if profile_data.get('fitness_goals'):
                    print(f"Setting fitness_goals: {profile_data['fitness_goals']}")
                    profile.set_fitness_goals(profile_data['fitness_goals'])
                
                if profile_data.get('injuries'):
                    print(f"Setting injuries: {profile_data['injuries']}")
                    profile.set_injuries(profile_data['injuries'])
                
                if profile_data.get('injury_details'):
                    profile.injury_details = profile_data['injury_details']
                
                if profile_data.get('medical_conditions'):
                    print(f"Setting medical_conditions: {profile_data['medical_conditions']}")
                    profile.set_medical_conditions(profile_data['medical_conditions'])
                
                if profile_data.get('medical_condition_details'):
                    profile.medical_condition_details = profile_data['medical_condition_details']
                
                if profile_data.get('equipment_access'):
                    print(f"Setting equipment_access: {profile_data['equipment_access']}")
                    profile.set_equipment_access(profile_data['equipment_access'])
                
                if profile_data.get('home_equipment'):
                    print(f"Setting home_equipment: {profile_data['home_equipment']}")
                    profile.set_home_equipment(profile_data['home_equipment'])
                
                db.session.add(profile)
                db.session.flush()  # Flush to ensure profile is in session before commit
                print(f"Profile created successfully for user {user.id}, profile ID: {profile.id}")
            except Exception as e:
                import traceback
                print(f"Error creating user profile: {e}")
                print(traceback.format_exc())
                # Don't fail registration if profile creation fails - user can complete profile later
                # Just log the error and continue
                db.session.rollback()
                # Re-add user since rollback removed it
                db.session.add(user)
                db.session.flush()
        
        db.session.commit()
        
        # Flask-JWT-Extended requires identity to be a string
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'language': user.language
            }
        }), 201
    except Exception as e:
        import traceback
        print(f"Error in register: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        try:
            user = User.query.filter_by(username=username).first()
            print(f"Login attempt for username: {username}")
            print(f"User found: {user is not None}")
            
            if user:
                print(f"User ID: {user.id}, Email: {user.email}")
                password_match = check_password_hash(user.password_hash, password)
                print(f"Password match: {password_match}")
                
                if password_match:
                    # Flask-JWT-Extended requires identity to be a string
                    access_token = create_access_token(identity=str(user.id))
                    print(f"Token created for user {user.id}, token (first 50 chars): {access_token[:50]}...")
                    return jsonify({
                        'access_token': access_token,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'language': user.language,
                            'role': user.role
                        }
                    }), 200
                else:
                    print(f"Password mismatch for user: {username}")
            else:
                print(f"User not found: {username}")
            
            return jsonify({'error': 'Invalid credentials'}), 401
        except Exception as db_error:
            print(f"Database error during login: {db_error}")
            import traceback
            print(traceback.format_exc())
            raise
    except Exception as e:
        import traceback
        print(f"Error in login: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/reset-demo-password', methods=['POST'])
def reset_demo_password():
    """Reset demo user password - for development only"""
    data = request.get_json()
    new_password = data.get('password', 'demo123')
    
    user = User.query.filter_by(username='demo').first()
    if not user:
        return jsonify({'error': 'Demo user not found'}), 404
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Demo user password reset',
        'username': 'demo',
        'password': new_password
    }), 200

@app.route('/api/user', methods=['GET', 'PUT'])
@jwt_required()
def get_user():
    try:
        # get_jwt_identity() returns a string, convert to int for database query
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        import traceback
        print(f"Error in get_user: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication failed'}), 401
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update username if provided
            if 'username' in data and data['username']:
                # Check if username is already taken by another user
                existing_user = User.query.filter(User.username == data['username'], User.id != user_id).first()
                if existing_user:
                    return jsonify({'error': 'Username already taken'}), 400
                user.username = data['username']
            
            # Update email if provided
            if 'email' in data and data['email']:
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['email']):
                    return jsonify({'error': 'Invalid email format'}), 400
                
                # Check if email is already taken by another user
                existing_user = User.query.filter(User.email == data['email'], User.id != user_id).first()
                if existing_user:
                    return jsonify({'error': 'Email already taken'}), 400
                user.email = data['email']
            
            db.session.commit()
            
            return jsonify({
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        except Exception as e:
            import traceback
            db.session.rollback()
            print(f"Error updating user: {e}")
            print(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    # GET method - Get user profile if exists
    profile_data = None
    try:
        from models import UserProfile
        # Use db.session.query() to avoid app context issues
        profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
        if profile:
            profile_data = {
                'age': profile.age,
                'weight': profile.weight,
                'height': profile.height,
                'gender': profile.gender,
                'training_level': profile.training_level,
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
                'preferred_intensity': profile.preferred_intensity,
                'profile_image': profile.profile_image if hasattr(profile, 'profile_image') else None
            }
    except Exception as e:
        print(f"Error getting user profile: {e}")
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'language': user.language,
        'role': user.role if hasattr(user, 'role') else 'member',
        'profile': profile_data
    }), 200

@app.route('/api/user/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    # @jwt_required() validates the token before this function runs
    # If token is invalid, invalid_token_callback is called
    # If token is valid, we can safely get user_id
    # get_jwt_identity() returns a string, convert to int for database query
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
    except Exception as e:
        import traceback
        print(f"Error getting user_id in user_profile: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication failed'}), 401
    
    if request.method == 'GET':
            try:
                # Import UserProfile - it should be available from models
                from models import UserProfile
                
                # Query profile using db.session.query() to avoid app context issues
                profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
                if not profile:
                    return jsonify({'error': 'Profile not found'}), 404
                
                # Safely get all profile data with error handling for each field
                try:
                    fitness_goals = profile.get_fitness_goals() if hasattr(profile, 'get_fitness_goals') else []
                except Exception as e:
                    print(f"Error getting fitness_goals: {e}")
                    fitness_goals = []
                
                try:
                    injuries = profile.get_injuries() if hasattr(profile, 'get_injuries') else []
                except Exception as e:
                    print(f"Error getting injuries: {e}")
                    injuries = []
                
                try:
                    medical_conditions = profile.get_medical_conditions() if hasattr(profile, 'get_medical_conditions') else []
                except Exception as e:
                    print(f"Error getting medical_conditions: {e}")
                    medical_conditions = []
                
                try:
                    equipment_access = profile.get_equipment_access() if hasattr(profile, 'get_equipment_access') else []
                except Exception as e:
                    print(f"Error getting equipment_access: {e}")
                    equipment_access = []
                
                try:
                    home_equipment = profile.get_home_equipment() if hasattr(profile, 'get_home_equipment') else []
                except Exception as e:
                    print(f"Error getting home_equipment: {e}")
                    home_equipment = []
                
                return jsonify({
                    'age': profile.age,
                    'weight': profile.weight,
                    'height': profile.height,
                    'gender': profile.gender or '',
                    'account_type': profile.account_type or '',
                    'training_level': profile.training_level or '',
                    'fitness_goals': fitness_goals,
                    'injuries': injuries,
                    'injury_details': profile.injury_details or '',
                    'medical_conditions': medical_conditions,
                    'medical_condition_details': profile.medical_condition_details or '',
                    'exercise_history_years': profile.exercise_history_years,
                    'exercise_history_description': profile.exercise_history_description or '',
                    'chest_circumference': profile.chest_circumference,
                    'waist_circumference': profile.waist_circumference,
                    'abdomen_circumference': profile.abdomen_circumference,
                    'arm_circumference': profile.arm_circumference,
                    'hip_circumference': profile.hip_circumference,
                    'thigh_circumference': profile.thigh_circumference,
                    'equipment_access': equipment_access,
                    'gym_access': profile.gym_access if profile.gym_access is not None else False,
                    'home_equipment': home_equipment,
                    'preferred_workout_time': profile.preferred_workout_time or '',
                    'workout_days_per_week': profile.workout_days_per_week,
                    'preferred_intensity': profile.preferred_intensity or '',
                    'profile_image': profile.profile_image if hasattr(profile, 'profile_image') and profile.profile_image else None
                }), 200
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"\n{'='*70}")
                print(f"ERROR in /api/user/profile GET: {e}")
                print(f"Error type: {type(e).__name__}")
                print(f"User ID: {user_id}")
                print(f"Traceback:")
                print(error_trace)
                print(f"{'='*70}\n")
                return jsonify({'error': f'Error loading profile: {str(e)}'}), 500
    
    elif request.method == 'PUT':
        try:
            from models import UserProfile
            import json as json_lib
            
            data = request.get_json()
            # Use db.session.query() to avoid app context issues
            profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                # Create new profile
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
            
            # Update basic info
            if 'age' in data:
                profile.age = data['age']
            if 'weight' in data:
                profile.weight = data['weight']
            if 'height' in data:
                profile.height = data['height']
            if 'gender' in data:
                profile.gender = data['gender']
            if 'account_type' in data:
                profile.account_type = data['account_type']
            if 'training_level' in data:
                profile.training_level = data['training_level']
            
            # Update body measurements
            if 'chest_circumference' in data:
                profile.chest_circumference = data['chest_circumference']
            if 'waist_circumference' in data:
                profile.waist_circumference = data['waist_circumference']
            if 'abdomen_circumference' in data:
                profile.abdomen_circumference = data['abdomen_circumference']
            if 'arm_circumference' in data:
                profile.arm_circumference = data['arm_circumference']
            if 'hip_circumference' in data:
                profile.hip_circumference = data['hip_circumference']
            if 'thigh_circumference' in data:
                profile.thigh_circumference = data['thigh_circumference']
            
            # Update JSON fields
            if 'fitness_goals' in data:
                profile.set_fitness_goals(data['fitness_goals'])
            if 'injuries' in data:
                profile.set_injuries(data['injuries'])
            if 'injury_details' in data:
                profile.injury_details = data['injury_details']
            if 'medical_conditions' in data:
                profile.set_medical_conditions(data['medical_conditions'])
            if 'medical_condition_details' in data:
                profile.medical_condition_details = data['medical_condition_details']
            if 'equipment_access' in data:
                profile.set_equipment_access(data['equipment_access'])
            if 'home_equipment' in data:
                profile.set_home_equipment(data['home_equipment'])
            
            # Update preferences
            if 'gym_access' in data:
                profile.gym_access = data['gym_access']
            if 'preferred_workout_time' in data:
                profile.preferred_workout_time = data['preferred_workout_time']
            if 'workout_days_per_week' in data:
                profile.workout_days_per_week = data['workout_days_per_week']
            if 'preferred_intensity' in data:
                profile.preferred_intensity = data['preferred_intensity']
            if 'exercise_history_years' in data:
                profile.exercise_history_years = data['exercise_history_years']
            if 'exercise_history_description' in data:
                profile.exercise_history_description = data['exercise_history_description']
            
            # Handle profile image (base64 encoded)
            if 'profile_image' in data and data['profile_image'] and data['profile_image'] != 'null':
                try:
                    # Save base64 image
                    image_data = data['profile_image']
                    if isinstance(image_data, str) and image_data.startswith('data:image'):
                        # Extract base64 data
                        header, encoded = image_data.split(',', 1)
                        image_bytes = base64.b64decode(encoded)
                        
                        # Generate filename
                        filename = f"profile_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        # Save file
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        
                        # Delete old image if exists
                        if hasattr(profile, 'profile_image') and profile.profile_image:
                            old_path = os.path.join(app.config['UPLOAD_FOLDER'], profile.profile_image)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Store filename in database (we'll need to add this column)
                        profile.profile_image = filename
                except Exception as e:
                    print(f"Error saving profile image: {e}")
            
            profile.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'profile': {
                    'age': profile.age,
                    'weight': profile.weight,
                    'height': profile.height,
                    'gender': profile.gender,
                    'training_level': profile.training_level,
                    'fitness_goals': profile.get_fitness_goals(),
                    'profile_image': profile.profile_image if hasattr(profile, 'profile_image') else None
                }
            }), 200
            
        except Exception as e:
            import traceback
            db.session.rollback()
            error_trace = traceback.format_exc()
            print(f"Error updating profile: {e}")
            print(error_trace)
            # Return more detailed error for debugging
            error_msg = str(e)
            if 'ForeignKey' in error_msg or 'foreign key' in error_msg.lower():
                error_msg = 'Database relationship error. Please contact support.'
            elif 'no such table' in error_msg.lower():
                error_msg = 'Database table not found. Please restart the server.'
            return jsonify({'error': error_msg, 'details': error_trace if app.debug else None}), 500

@app.route('/api/uploads/voice_notes/<path:filename>', methods=['GET'])
def get_voice_note(filename):
    """Serve uploaded voice note file (trainer notes)."""
    try:
        from flask import send_from_directory
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'voice_notes')
        return send_from_directory(upload_dir, filename, as_attachment=False)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/uploads/exercises/<path:filename>', methods=['GET'])
def get_exercise_upload(filename):
    """Serve uploaded exercise media (videos, voice). Path e.g. videos/xxx.mp4 or voice/xxx.webm."""
    try:
        from flask import send_from_directory
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'exercises')
        return send_from_directory(upload_dir, filename, as_attachment=False)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/user/profile/image/<filename>', methods=['GET'])
@jwt_required()
def get_profile_image(filename):
    """Serve profile image file"""
    try:
        # get_jwt_identity() returns a string, convert to int for database query
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        
        from flask import send_from_directory
        # Secure filename check
        if '..' in filename or '/' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving image: {e}")
        return jsonify({'error': 'Image not found'}), 404

@app.route('/api/exercises', methods=['GET', 'POST'])
@jwt_required()
def exercises():
    try:
        # get_jwt_identity() returns a string, convert to int for database query
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
    except Exception as e:
        print(f"Error in exercises auth: {e}")
        return jsonify({'error': 'Authentication failed'}), 401
    
    if request.method == 'GET':
        exercises = UserExercise.query.filter_by(user_id=user_id).order_by(UserExercise.date.desc()).all()
        return jsonify([{
            'id': ex.id,
            'exercise_name': ex.exercise_name,
            'exercise_type': ex.exercise_type,
            'duration': ex.duration,
            'calories_burned': ex.calories_burned,
            'date': ex.date.isoformat() if ex.date else None,
            'notes': ex.notes
        } for ex in exercises]), 200
    
    if request.method == 'POST':
        data = request.get_json()
        exercise = UserExercise(
            user_id=user_id,
            exercise_name=data.get('exercise_name'),
            exercise_type=data.get('exercise_type'),
            duration=data.get('duration'),
            calories_burned=data.get('calories_burned'),
            notes=data.get('notes')
        )
        db.session.add(exercise)
        db.session.commit()
        return jsonify({'id': exercise.id, 'message': 'Exercise added successfully'}), 201

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        # get_jwt_identity() returns a string, convert to int for database query
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        data = request.get_json()
        message = data.get('message')
        local_time = data.get('local_time')  # Get local time from browser
        user = db.session.get(User, user_id)
        user_language = user.language if user else 'fa'
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # AI agent response (simplified - you can integrate OpenAI or other AI service)
        # For now, we'll create a simple response system
        response = generate_ai_response(message, user_id, user_language, local_time)
        
        # Session: use provided session_id or create new conversation
        session_id = (data.get('session_id') or '').strip() or None
        if not session_id:
            session_id = str(uuid.uuid4())
        # Save chat history
        chat_entry = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response
        )
        db.session.add(chat_entry)
        # Ensure ChatSession row exists for this conversation (for optional rename)
        existing = ChatSession.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not existing:
            db.session.add(ChatSession(session_id=session_id, user_id=user_id, title=None))
        db.session.commit()
        
        return jsonify({
            'response': response,
            'timestamp': chat_entry.timestamp.isoformat(),
            'session_id': session_id
        }), 200
    except Exception as e:
        # This is for errors after authentication
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in chat endpoint: {str(e)}")
        print("=" * 50)
        print("FULL TRACEBACK:")
        print(error_trace)
        print("=" * 50)
        db.session.rollback()
        
        # Check if it's an auth error
        if 'jwt' in str(e).lower() or 'token' in str(e).lower() or 'unauthorized' in str(e).lower():
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Return a simple error response that the frontend can handle
        user = None
        user_language = 'fa'
        try:
            # get_jwt_identity() returns a string, convert to int for database query
            user_id_str = get_jwt_identity()
            if user_id_str:
                user_id = int(user_id_str)
                user = db.session.get(User, user_id)
                if user:
                    user_language = user.language
        except:
            pass
        
        error_message_fa = "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید."
        error_message_en = "Sorry, an error occurred. Please try again."
        
        return jsonify({
            'response': error_message_fa if user_language == 'fa' else error_message_en,
            'timestamp': datetime.utcnow().isoformat()
        }), 200  # Return 200 so frontend doesn't treat it as an error

@app.route('/api/chat/conversations', methods=['GET'])
@jwt_required()
def chat_conversations():
    """List conversations (sessions) for the user: session_id, preview, last_at, message_count."""
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.asc()).all()
        # Group by session_id (null/empty = legacy: each row is its own "conversation")
        by_session = {}
        for c in chats:
            sid = c.session_id or f'_legacy_{c.id}'
            if sid not in by_session:
                by_session[sid] = {'session_id': c.session_id or sid, 'messages': [], 'last_at': c.timestamp}
            by_session[sid]['messages'].append({'id': c.id, 'message': c.message, 'response': c.response, 'timestamp': c.timestamp.isoformat()})
            by_session[sid]['last_at'] = max(by_session[sid]['last_at'], c.timestamp)
        # Fetch custom titles from ChatSession
        session_ids = list(by_session.keys())
        titles = {s.session_id: (s.title or '').strip() for s in ChatSession.query.filter(
            ChatSession.session_id.in_(session_ids),
            ChatSession.user_id == user_id
        ).all() if (s.title or '').strip()}
        out = []
        for sid, data in by_session.items():
            first_user = next((m['message'] for m in data['messages'] if m.get('message')), '')
            preview = (first_user[:60] + '...') if len(first_user) > 60 else first_user
            display_title = titles.get(sid) or preview or '(No message)'
            out.append({
                'session_id': data['session_id'] if data['session_id'] and not str(data['session_id']).startswith('_legacy') else sid,
                'preview': preview or '(No message)',
                'title': display_title,
                'last_at': data['last_at'].isoformat(),
                'message_count': len(data['messages']) * 2
            })
        out.sort(key=lambda x: x['last_at'], reverse=True)
        return jsonify(out), 200
    except Exception as e:
        import traceback
        print(f"Error in chat_conversations: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication failed'}), 401


@app.route('/api/chat/conversations/<session_id>', methods=['PATCH'])
@jwt_required()
def chat_conversation_rename(session_id):
    """Rename a conversation (set custom title). session_id can be uuid or _legacy_<id>."""
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        session_id = (session_id or '').strip()
        if not session_id:
            return jsonify({'error': 'session_id required'}), 400
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()[:256]
        # Ensure user owns this conversation
        if session_id.startswith('_legacy_'):
            try:
                legacy_id = int(session_id.replace('_legacy_', ''))
                exists = ChatHistory.query.filter_by(user_id=user_id, id=legacy_id).first()
            except ValueError:
                exists = None
        else:
            exists = ChatHistory.query.filter_by(user_id=user_id, session_id=session_id).first()
        if not exists:
            return jsonify({'error': 'Conversation not found'}), 404
        row = ChatSession.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not row:
            row = ChatSession(session_id=session_id, user_id=user_id, title=title or None)
            db.session.add(row)
        else:
            row.title = title or None
        db.session.commit()
        return jsonify({'session_id': session_id, 'title': row.title or ''}), 200
    except Exception as e:
        import traceback
        print(f"Error in chat_conversation_rename: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication failed'}), 401


@app.route('/api/chat/history', methods=['GET'])
@jwt_required()
def chat_history():
    """Get chat history. If session_id query param is set, return only that conversation."""
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        session_id = request.args.get('session_id', '').strip() or None
        q = ChatHistory.query.filter_by(user_id=user_id)
        if session_id:
            if session_id.startswith('_legacy_'):
                try:
                    legacy_id = int(session_id.replace('_legacy_', ''))
                    q = q.filter(ChatHistory.id == legacy_id)
                except ValueError:
                    pass
            else:
                q = q.filter_by(session_id=session_id)
        chats = q.order_by(ChatHistory.timestamp.asc()).all()
        return jsonify([{
            'id': chat.id,
            'session_id': chat.session_id,
            'message': chat.message,
            'response': chat.response,
            'timestamp': chat.timestamp.isoformat()
        } for chat in chats]), 200
    except Exception as e:
        import traceback
        print(f"Error in chat_history: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/api/nutrition/plans', methods=['GET', 'POST'])
@jwt_required()
def nutrition_plans():
    from models import NutritionPlan
    try:
        # get_jwt_identity() returns a string, convert to int for database query
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
    except Exception as e:
        print(f"Error in nutrition_plans auth: {e}")
        return jsonify({'error': 'Authentication failed'}), 401
    
    if request.method == 'GET':
        plan_type = request.args.get('type', '2week')
        plans = NutritionPlan.query.filter_by(
            user_id=user_id,
            plan_type=plan_type
        ).order_by(NutritionPlan.day, NutritionPlan.id).all()
        
        return jsonify([{
            'id': plan.id,
            'day': plan.day,
            'meal_type': plan.meal_type,
            'food_item': plan.food_item,
            'calories': plan.calories,
            'protein': plan.protein,
            'carbs': plan.carbs,
            'fats': plan.fats,
            'notes': plan.notes
        } for plan in plans]), 200
    
    if request.method == 'POST':
        data = request.get_json()
        plan = NutritionPlan(
            user_id=user_id,
            plan_type=data.get('plan_type', '2week'),
            day=data.get('day'),
            meal_type=data.get('meal_type'),
            food_item=data.get('food_item'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            carbs=data.get('carbs'),
            fats=data.get('fats'),
            notes=data.get('notes')
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify({'id': plan.id, 'message': 'Nutrition plan added successfully'}), 201

@app.route('/api/tips', methods=['GET'])
def tips():
    language = request.args.get('language', 'fa')
    tips = Tip.query.all()
    
    return jsonify([{
        'id': tip.id,
        'title': tip.title_fa if language == 'fa' else tip.title_en,
        'content': tip.content_fa if language == 'fa' else tip.content_en,
        'category': tip.category,
        'created_at': tip.created_at.isoformat() if tip.created_at else None
    } for tip in tips]), 200

@app.route('/api/injuries', methods=['GET'])
def injuries():
    language = request.args.get('language', 'fa')
    injuries = Injury.query.all()
    
    return jsonify([{
        'id': injury.id,
        'title': injury.title_fa if language == 'fa' else injury.title_en,
        'description': injury.description_fa if language == 'fa' else injury.description_en,
        'prevention': injury.prevention_fa if language == 'fa' else injury.prevention_en,
        'treatment': injury.treatment_fa if language == 'fa' else injury.treatment_en,
        'created_at': injury.created_at.isoformat() if injury.created_at else None
    } for injury in injuries]), 200

def generate_ai_response(message, user_id, language, local_time=None):
    """Generate AI response based on user message and context"""
    # Initialize defaults
    user_name = 'کاربر'
    recommended_exercises = []
    user_injuries = []
    user_profile = None
    missing_profile_fields = []
    
    # Safety check for message
    if not message or not isinstance(message, str):
        print(f"WARNING: Invalid message received: {message}")
        if language == 'fa':
            return "لطفاً پیام خود را دوباره ارسال کنید."
        else:
            return "Please send your message again."
    
    try:
        # Get user info
        user = db.session.get(User, user_id)
        user_name = user.username if user else 'کاربر'
    except Exception as e:
        print(f"Error getting user: {e}")
    
    # Import Exercise library model
    try:
        from models import Exercise as ExerciseLibrary, UserProfile
        try:
            # Get user profile for context
            # Use db.session.query() to avoid app context issues
            user_profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
            if user_profile:
                try:
                    user_injuries = user_profile.get_injuries()
                except:
                    user_injuries = []
                
                # Check for missing profile fields
                missing_profile_fields = []
                if not user_profile.age:
                    missing_profile_fields.append('age')
                if not user_profile.weight:
                    missing_profile_fields.append('weight')
                if not user_profile.height:
                    missing_profile_fields.append('height')
                if not user_profile.gender:
                    missing_profile_fields.append('gender')
                if not user_profile.training_level:
                    missing_profile_fields.append('training_level')
                if not user_profile.get_fitness_goals():
                    missing_profile_fields.append('fitness_goals')
                if not user_profile.workout_days_per_week:
                    missing_profile_fields.append('workout_days_per_week')
            else:
                # No profile exists - all fields are missing
                missing_profile_fields = ['age', 'weight', 'height', 'gender', 'training_level', 'fitness_goals', 'workout_days_per_week']
        except Exception as e:
            print(f"Error getting user profile: {e}")
            user_profile = None
            missing_profile_fields = ['age', 'weight', 'height', 'gender', 'training_level', 'fitness_goals', 'workout_days_per_week']
        
        # Get recommended exercises from library
        try:
            exercise_library_query = ExerciseLibrary.query
            if user_profile:
                if not user_profile.gym_access:
                    exercise_library_query = exercise_library_query.filter_by(category='functional_home')
                if user_profile.training_level:
                    if user_profile.training_level == 'beginner':
                        exercise_library_query = exercise_library_query.filter_by(level='beginner')
            if user_injuries:
                for injury in user_injuries:
                    # Use contains with proper JSON format
                    exercise_library_query = exercise_library_query.filter(
                        ~ExerciseLibrary.injury_contraindications.contains(f'"{injury}"')
                    )
            recommended_exercises = exercise_library_query.limit(5).all()
        except Exception as e:
            import traceback
            print(f"Error querying exercise library: {e}")
            print(traceback.format_exc())
            recommended_exercises = []
    except ImportError as e:
        print(f"Import error (models not available): {e}")
        recommended_exercises = []
    except Exception as e:
        import traceback
        print(f"Error in exercise library setup: {e}")
        print(traceback.format_exc())
        recommended_exercises = []
    
    # Get user's exercise history and nutrition plans for context
    try:
        exercises = UserExercise.query.filter_by(user_id=user_id).order_by(UserExercise.date.desc()).limit(10).all()
    except Exception as e:
        print(f"Error querying exercise history: {e}")
        exercises = []
    
    try:
        from models import NutritionPlan
        nutrition_plans = NutritionPlan.query.filter_by(user_id=user_id).limit(5).all()
    except Exception as e:
        print(f"Error querying nutrition plans: {e}")
        nutrition_plans = []
    
    # Analyze recent exercises
    recent_exercises = exercises[:5] if exercises else []
    exercise_summary = []
    if recent_exercises:
        for ex in recent_exercises:
            if ex.exercise_name:
                exercise_summary.append(ex.exercise_name)
    
    # Analyze nutrition plans
    nutrition_summary = []
    if nutrition_plans:
        unique_foods = set()
        for plan in nutrition_plans:
            if plan.food_item:
                unique_foods.add(plan.food_item)
        nutrition_summary = list(unique_foods)[:5]
    
    # Get time greeting based on local time
    time_greeting = ""
    if local_time:
        try:
            from datetime import datetime
            # Parse local time (assuming ISO format or timestamp)
            if isinstance(local_time, str):
                local_dt = datetime.fromisoformat(local_time.replace('Z', '+00:00'))
            else:
                local_dt = datetime.fromtimestamp(local_time / 1000) if local_time > 1000000000000 else datetime.fromtimestamp(local_time)
            
            hour = local_dt.hour
            if language == 'fa':
                if 5 <= hour < 12:
                    time_greeting = "صبح بخیر"
                elif 12 <= hour < 17:
                    time_greeting = "ظهر بخیر"
                elif 17 <= hour < 20:
                    time_greeting = "عصر بخیر"
                else:
                    time_greeting = "شب بخیر"
            else:
                if 5 <= hour < 12:
                    time_greeting = "Good morning"
                elif 12 <= hour < 17:
                    time_greeting = "Good afternoon"
                elif 17 <= hour < 20:
                    time_greeting = "Good evening"
                else:
                    time_greeting = "Good night"
        except:
            pass
    
    message_lower = message.lower() if message else ""
    
    # Debug logging
    print(f"DEBUG: generate_ai_response called with message='{message}', language='{language}', user_id={user_id}")
    
    try:
        # ----- Admin/Assistant: add movement note (AI can add notes for admin) -----
        user_role = getattr(user, 'role', None) if user else None
        if user_role in ('admin', 'assistant'):
            import re
            from models import Exercise as ExerciseModel
            exercise_name = None
            note_text = None
            # Persian: "یادداشت برای حرکت X اضافه کن: متن" or "یادداشت برای X: متن" or "یادداشت حرکت X: متن"
            if language == 'fa':
                m = re.search(r'یادداشت\s*(?:برای\s*)?(?:حرکت\s*)?(.+?)\s*(?:اضافه\s*کن\s*)?[:\s]+(.+)', message, re.DOTALL)
                if m:
                    exercise_name = m.group(1).strip()
                    note_text = m.group(2).strip()
                if not exercise_name and ('یادداشت' in message and 'حرکت' in message):
                    # Fallback: split by : and take last part as note, before that find movement name
                    parts = message.split(':', 1)
                    if len(parts) == 2:
                        note_text = parts[1].strip()
                        left = parts[0].replace('یادداشت', '').replace('برای', '').replace('حرکت', '').replace('اضافه کن', '').strip()
                        if left:
                            exercise_name = left
            else:
                # English: "add note to movement X: text" or "add note to X: text"
                m = re.search(r'add\s+note\s+to\s+(?:movement\s+)?(.+?)\s*[:\-]\s*(.+)', message_lower, re.DOTALL)
                if m:
                    exercise_name = m.group(1).strip()
                    note_text = m.group(2).strip()
            if exercise_name and note_text:
                ex = db.session.query(ExerciseModel).filter(
                    (ExerciseModel.name_fa == exercise_name) | (ExerciseModel.name_en == exercise_name)
                ).first()
                if ex:
                    if language == 'fa':
                        ex.trainer_notes_fa = (ex.trainer_notes_fa or '') + '\n' + note_text if ex.trainer_notes_fa else note_text
                    else:
                        ex.trainer_notes_en = (ex.trainer_notes_en or '') + '\n' + note_text if ex.trainer_notes_en else note_text
                    db.session.commit()
                    if language == 'fa':
                        return f"یادداشت برای حرکت «{ex.name_fa or ex.name_en}» ذخیره شد. این یادداشت در برنامه تمرینی اعضا نمایش داده می‌شود. می‌توانید در تب «اطلاعات حرکات تمرینی» آن را ویرایش یا با دکمه «اضافه به برنامه‌های اعضا» به همه برنامه‌ها اعمال کنید."
                    else:
                        return f"Note for movement «{ex.name_en or ex.name_fa}» saved. It will be shown in members' training program. You can edit it in the «Training Movement Info» tab or use «Add to members' programs» to apply to all programs."
                else:
                    if language == 'fa':
                        return f"حرکتی با نام «{exercise_name}» در کتابخانه تمرینات پیدا نشد. لطفاً نام دقیق حرکت را از تب کتابخانه تمرینات وارد کنید."
                    else:
                        return f"No movement named «{exercise_name}» found in the exercise library. Please use the exact name from the Exercise Library tab."
        
        if language == 'fa':
            # Greeting
            if any(word in message for word in ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'شب بخیر']):
                context_info = ""
                
                # User profile context
                if user_profile:
                    profile_info = []
                    if user_profile.age:
                        profile_info.append(f"{user_profile.age} ساله")
                    if user_profile.gender:
                        gender_text = "آقا" if user_profile.gender == 'male' else "خانم"
                        profile_info.append(gender_text)
                    if user_profile.training_level:
                        level_text = {
                            'beginner': 'مبتدی',
                            'intermediate': 'متوسط',
                            'advanced': 'پیشرفته'
                        }.get(user_profile.training_level, user_profile.training_level)
                        profile_info.append(f"سطح {level_text}")
                    
                    if profile_info:
                        context_info = f"سلام {user_name} {time_greeting}! "
                        context_info += f"می‌بینم که شما {' و '.join(profile_info)} هستید. "
                    else:
                        context_info = f"سلام {user_name} {time_greeting}! "
                else:
                    context_info = f"سلام {user_name} {time_greeting}! "
                
                # Exercise history
                if exercises:
                    context_info += f"شما {len(exercises)} تمرین ثبت کرده‌اید. "
                if nutrition_plans:
                    context_info += f"همچنین برنامه تغذیه‌ای دارید. "
                
                # User profile details
                profile_details = ""
                if user_profile:
                    if user_profile.fitness_goals:
                        goals = user_profile.get_fitness_goals()
                        if goals:
                            goals_fa = {
                                'weight_loss': 'کاهش وزن',
                                'muscle_gain': 'افزایش عضله',
                                'strength': 'قدرت',
                                'endurance': 'استقامت',
                                'flexibility': 'انعطاف‌پذیری'
                            }
                            goals_text = [goals_fa.get(g, g) for g in goals]
                            profile_details += f"اهداف شما: {', '.join(goals_text)}. "
                    
                    if user_profile.workout_days_per_week:
                        profile_details += f"{user_profile.workout_days_per_week} روز در هفته تمرین می‌کنید. "
                    
                    if user_injuries:
                        injuries_fa = {
                            'knee': 'زانو',
                            'shoulder': 'شانه',
                            'lower_back': 'کمر',
                            'ankle': 'مچ پا',
                            'wrist': 'مچ دست'
                        }
                        injuries_text = [injuries_fa.get(i, i) for i in user_injuries]
                        profile_details += f"توجه: شما مشکل {', '.join(injuries_text)} دارید، بنابراین تمرینات مناسب را پیشنهاد می‌دهم. "
                
                # Add profile completion suggestion if profile is incomplete
                profile_suggestion = ""
                if missing_profile_fields:
                    important_fields = []
                    if 'age' in missing_profile_fields:
                        important_fields.append('سن')
                    if 'gender' in missing_profile_fields:
                        important_fields.append('جنسیت')
                    if 'training_level' in missing_profile_fields:
                        important_fields.append('سطح تمرین')
                    if 'fitness_goals' in missing_profile_fields:
                        important_fields.append('اهداف تناسب اندام')
                    
                    if important_fields:
                        profile_suggestion = f"\n\n💡 نکته: برای دریافت برنامه‌های شخصی‌تر، لطفاً اطلاعات پروفایل خود را در تب 'پروفایل' تکمیل کنید. اطلاعات مهم: {', '.join(important_fields)}"
                
                return f"{context_info}من دستیار هوشمند آلفا فیت هستم. {profile_details}چگونه می‌توانم به شما کمک کنم؟ می‌توانم در مورد برنامه تمرینی، تغذیه، یا هر سوال دیگری کمک کنم.{profile_suggestion}"
            
            # Fitness plan request
            elif any(word in message for word in ['برنامه', 'تمرین', 'ورزش', 'workout', 'plan']):
                print(f"DEBUG: Matched fitness plan request for message: '{message}'")
                exercise_suggestions = ""
                if recommended_exercises:
                    try:
                        exercise_names = []
                        for ex in recommended_exercises[:3]:
                            if hasattr(ex, 'name_fa') and ex.name_fa:
                                exercise_names.append(ex.name_fa)
                            elif hasattr(ex, 'name') and ex.name:
                                exercise_names.append(ex.name)
                        if exercise_names:
                            exercise_suggestions = f"\n\nتمرینات پیشنهادی برای شما:\n{chr(10).join(['- ' + name for name in exercise_names])}"
                    except Exception as e:
                        import traceback
                        print(f"Error getting exercise names: {e}")
                        print(traceback.format_exc())
                        exercise_suggestions = ""
                
                # Use user profile info
                profile_context = ""
                try:
                    if user_profile:
                        if user_profile.workout_days_per_week:
                            profile_context += f"با توجه به اینکه {user_profile.workout_days_per_week} روز در هفته تمرین می‌کنید، "
                        if user_profile.preferred_workout_time:
                            time_fa = {
                                'morning': 'صبح',
                                'afternoon': 'ظهر',
                                'evening': 'عصر'
                            }.get(user_profile.preferred_workout_time, user_profile.preferred_workout_time)
                            profile_context += f"و ترجیح می‌دهید در {time_fa} تمرین کنید، "
                        if user_profile.training_level:
                            level_fa = {
                                'beginner': 'مبتدی',
                                'intermediate': 'متوسط',
                                'advanced': 'پیشرفته'
                            }.get(user_profile.training_level, user_profile.training_level)
                            profile_context += f"با سطح {level_fa} شما، "
                except Exception as e:
                    print(f"Error building profile context: {e}")
                    profile_context = ""
                
                try:
                    response_text = f"بله {user_name}! می‌توانم یک برنامه تمرینی شخصی برای شما ایجاد کنم. {profile_context}لطفاً بگویید:\n- هدف شما چیست؟ (کاهش وزن، افزایش عضله، تناسب اندام عمومی)\n- چه نوع تمریناتی را ترجیح می‌دهید؟ (کاردیو، قدرتی، ترکیبی)\n\nبر اساس تاریخچه شما، می‌توانم برنامه‌ای متناسب با فعالیت‌های قبلی‌تان پیشنهاد دهم.{exercise_suggestions}"
                    print(f"DEBUG: Returning fitness plan response (length: {len(response_text)})")
                    return response_text
                except Exception as e:
                    import traceback
                    print(f"Error formatting response: {e}")
                    print(traceback.format_exc())
                    fallback_response = f"بله {user_name}! می‌توانم یک برنامه تمرینی شخصی برای شما ایجاد کنم. لطفاً بگویید:\n- هدف شما چیست؟ (کاهش وزن، افزایش عضله، تناسب اندام عمومی)\n- چه نوع تمریناتی را ترجیح می‌دهید؟ (کاردیو، قدرتی، ترکیبی)"
                    print(f"DEBUG: Returning fallback response")
                    return fallback_response
            
            # Nutrition request
            elif any(word in message for word in ['تغذیه', 'غذا', 'رژیم', 'nutrition', 'diet', 'meal']):
                context_nutrition = ""
                if nutrition_summary:
                    context_nutrition = f"بر اساس برنامه فعلی شما که شامل {', '.join(nutrition_summary[:3])} است، "
                return f"{context_nutrition}می‌توانم یک برنامه تغذیه‌ای ۲ یا ۴ هفته‌ای برای شما ایجاد کنم. لطفاً بگویید:\n- هدف شما چیست؟ (کاهش وزن، افزایش وزن، حفظ وزن)\n- آیا محدودیت غذایی خاصی دارید؟\n- ترجیح می‌دهید برنامه ۲ هفته‌ای باشد یا ۴ هفته‌ای؟"
            
            # Exercise history
            elif any(word in message for word in ['تاریخچه', 'تمرینات قبلی', 'history', 'past']):
                if exercise_summary:
                    return f"بر اساس تاریخچه شما، تمرینات اخیر شما شامل: {', '.join(exercise_summary)} است. می‌توانم بر اساس این اطلاعات، پیشنهادات بهتری برای ادامه مسیر شما ارائه دهم."
                else:
                    return "شما هنوز تمرینی ثبت نکرده‌اید. می‌توانم به شما کمک کنم تا برنامه تمرینی خود را شروع کنید!"
            
            # Injury/health
            elif any(word in message for word in ['آسیب', 'درد', 'injury', 'pain', 'hurt']):
                return "اگر دچار آسیب یا درد شده‌اید، مهم است که به پزشک یا فیزیوتراپیست مراجعه کنید. می‌توانم اطلاعات عمومی در مورد آسیب‌های رایج ورزشی و روش‌های پیشگیری را در بخش 'آسیب‌ها' به شما ارائه دهم."
            
            # Profile-related questions
            elif any(word in message for word in ['پروفایل', 'اطلاعات من', 'پروفایلم', 'profile', 'my info', 'my profile']):
                if missing_profile_fields:
                    missing_fields_fa = {
                        'age': 'سن',
                        'weight': 'وزن',
                        'height': 'قد',
                        'gender': 'جنسیت',
                        'training_level': 'سطح تمرین',
                        'fitness_goals': 'اهداف تناسب اندام',
                        'workout_days_per_week': 'روزهای تمرین در هفته',
                        'preferred_workout_time': 'زمان ترجیحی تمرین',
                        'injuries': 'آسیب‌ها'
                    }
                    missing_list = [missing_fields_fa.get(f, f) for f in missing_profile_fields if f in missing_fields_fa]
                    
                    return f"سلام {user_name}! می‌بینم که پروفایل شما کامل نیست. برای دریافت برنامه‌های شخصی‌تر و توصیه‌های دقیق‌تر، لطفاً به تب 'پروفایل' بروید و اطلاعات زیر را تکمیل کنید:\n\n" + \
                           "\n".join([f"• {field}" for field in missing_list]) + \
                           "\n\nپس از تکمیل پروفایل، می‌توانم برنامه‌های تمرینی و تغذیه‌ای دقیق‌تری برای شما ایجاد کنم!"
                else:
                    # Profile is complete
                    profile_summary = f"پروفایل شما کامل است! "
                    if user_profile:
                        if user_profile.age and user_profile.weight and user_profile.height:
                            bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
                            profile_summary += f"شاخص توده بدنی (BMI) شما: {bmi:.1f}. "
                        if user_profile.training_level:
                            profile_summary += f"سطح شما: {user_profile.training_level}. "
                    return f"{profile_summary}اگر می‌خواهید اطلاعات پروفایل خود را تغییر دهید، به تب 'پروفایل' بروید و روی دکمه 'ویرایش' کلیک کنید."
            
            # Questions about specific profile fields
            elif any(word in message for word in ['سن', 'age', 'چند سال', 'how old']):
                if user_profile and user_profile.age:
                    return f"سن شما در پروفایل: {user_profile.age} سال است. اگر می‌خواهید آن را تغییر دهید، به تب 'پروفایل' بروید."
                else:
                    return "شما هنوز سن خود را در پروفایل ثبت نکرده‌اید. لطفاً به تب 'پروفایل' بروید و سن خود را وارد کنید. این اطلاعات به من کمک می‌کند تا برنامه‌های مناسب‌تری برای شما ایجاد کنم."
            
            elif any(word in message for word in ['وزن', 'weight', 'چقدر وزن', 'how much do you weigh']):
                if user_profile and user_profile.weight:
                    return f"وزن شما در پروفایل: {user_profile.weight} کیلوگرم است. اگر می‌خواهید آن را تغییر دهید، به تب 'پروفایل' بروید."
                else:
                    return "شما هنوز وزن خود را در پروفایل ثبت نکرده‌اید. لطفاً به تب 'پروفایل' بروید و وزن خود را وارد کنید. این اطلاعات برای محاسبه کالری و ایجاد برنامه تغذیه‌ای ضروری است."
            
            elif any(word in message for word in ['قد', 'height', 'چقدر قد', 'how tall']):
                if user_profile and user_profile.height:
                    return f"قد شما در پروفایل: {user_profile.height} سانتی‌متر است. اگر می‌خواهید آن را تغییر دهید، به تب 'پروفایل' بروید."
                else:
                    return "شما هنوز قد خود را در پروفایل ثبت نکرده‌اید. لطفاً به تب 'پروفایل' بروید و قد خود را وارد کنید. این اطلاعات برای محاسبه BMI و ایجاد برنامه مناسب ضروری است."
            
            elif any(word in message for word in ['سطح', 'level', 'مبتدی', 'beginner', 'advanced', 'پیشرفته']):
                if user_profile and user_profile.training_level:
                    level_text = {
                        'beginner': 'مبتدی',
                        'intermediate': 'متوسط',
                        'advanced': 'پیشرفته'
                    }.get(user_profile.training_level, user_profile.training_level)
                    return f"سطح تمرین شما در پروفایل: {level_text} است. اگر می‌خواهید آن را تغییر دهید، به تب 'پروفایل' بروید."
                else:
                    return "شما هنوز سطح تمرین خود را در پروفایل مشخص نکرده‌اید. لطفاً به تب 'پروفایل' بروید و سطح خود را انتخاب کنید (مبتدی، متوسط، یا پیشرفته). این به من کمک می‌کند تا تمرینات مناسب را پیشنهاد دهم."
            
            elif any(word in message for word in ['هدف', 'goals', 'اهداف', 'چه هدفی']):
                if user_profile:
                    goals = user_profile.get_fitness_goals()
                    if goals:
                        goals_fa = {
                            'weight_loss': 'کاهش وزن',
                            'muscle_gain': 'افزایش عضله',
                            'strength': 'قدرت',
                            'endurance': 'استقامت',
                            'flexibility': 'انعطاف‌پذیری'
                        }
                        goals_text = [goals_fa.get(g, g) for g in goals]
                        return f"اهداف تناسب اندام شما: {', '.join(goals_text)}. اگر می‌خواهید آنها را تغییر دهید، به تب 'پروفایل' بروید."
                    else:
                        return "شما هنوز اهداف تناسب اندام خود را در پروفایل مشخص نکرده‌اید. لطفاً به تب 'پروفایل' بروید و اهداف خود را انتخاب کنید (مثلاً کاهش وزن، افزایش عضله، قدرت، استقامت، یا انعطاف‌پذیری)."
                else:
                    return "لطفاً ابتدا پروفایل خود را در تب 'پروفایل' تکمیل کنید و اهداف تناسب اندام خود را مشخص کنید."
            
            # General help
            else:
                suggestions = []
                if missing_profile_fields:
                    suggestions.append("تکمیل پروفایل برای دریافت برنامه‌های شخصی‌تر")
                if not exercises:
                    suggestions.append("شروع یک برنامه تمرینی")
                if not nutrition_plans:
                    suggestions.append("ایجاد برنامه تغذیه‌ای")
                suggestions.append("دریافت نکات و پیشنهادات")
                
                profile_note = ""
                if missing_profile_fields:
                    profile_note = "\n\n💡 پیشنهاد: برای دریافت برنامه‌های دقیق‌تر، ابتدا پروفایل خود را در تب 'پروفایل' تکمیل کنید."
                
                return f"متوجه شدم. من می‌توانم در موارد زیر به شما کمک کنم:\n- تکمیل پروفایل\n- ایجاد برنامه تمرینی شخصی\n- برنامه‌ریزی تغذیه‌ای\n- پاسخ به سوالات شما در مورد تناسب اندام\n- بررسی تاریخچه تمرینات شما\n\nلطفاً سوال خود را با جزئیات بیشتری مطرح کنید یا یکی از موارد بالا را انتخاب کنید.{profile_note}"
        
        else:  # English
            # Greeting
            if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'good night']):
                context_info = ""
                
                # User profile context
                if user_profile:
                    profile_info = []
                    if user_profile.age:
                        profile_info.append(f"{user_profile.age} years old")
                    if user_profile.gender:
                        profile_info.append(user_profile.gender)
                    if user_profile.training_level:
                        profile_info.append(f"{user_profile.training_level} level")
                    
                    if profile_info:
                        context_info = f"Hello {user_name}! {time_greeting}! "
                        context_info += f"I see you're {' and '.join(profile_info)}. "
                    else:
                        context_info = f"Hello {user_name}! {time_greeting}! "
                else:
                    context_info = f"Hello {user_name}! {time_greeting}! "
                
                # Exercise history
                if exercises:
                    context_info += f"You have {len(exercises)} recorded exercises. "
                if nutrition_plans:
                    context_info += f"You also have a nutrition plan. "
                
                # User profile details
                profile_details = ""
                if user_profile:
                    if user_profile.fitness_goals:
                        goals = user_profile.get_fitness_goals()
                        if goals:
                            profile_details += f"Your goals: {', '.join(goals)}. "
                    
                    if user_profile.workout_days_per_week:
                        profile_details += f"You work out {user_profile.workout_days_per_week} days per week. "
                    
                    if user_injuries:
                        profile_details += f"Note: You have {', '.join(user_injuries)} concerns, so I'll suggest appropriate exercises. "
                
                # Add profile completion suggestion if profile is incomplete
                profile_suggestion = ""
                if missing_profile_fields:
                    important_fields = []
                    if 'age' in missing_profile_fields:
                        important_fields.append('age')
                    if 'gender' in missing_profile_fields:
                        important_fields.append('gender')
                    if 'training_level' in missing_profile_fields:
                        important_fields.append('training level')
                    if 'fitness_goals' in missing_profile_fields:
                        important_fields.append('fitness goals')
                    
                    if important_fields:
                        profile_suggestion = f"\n\n💡 Tip: For more personalized plans, please complete your profile information in the 'Profile' tab. Important fields: {', '.join(important_fields)}"
                
                return f"{context_info}I'm AlphaFit AI assistant. {profile_details}How can I help you today? I can assist with workout plans, nutrition, or answer any fitness-related questions.{profile_suggestion}"
            
            # Fitness plan request
            elif any(word in message_lower for word in ['plan', 'workout', 'exercise', 'training']):
                exercise_suggestions = ""
                if recommended_exercises:
                    try:
                        exercise_names = [ex.name_en for ex in recommended_exercises[:3] if hasattr(ex, 'name_en')]
                        if exercise_names:
                            exercise_suggestions = f"\n\nRecommended exercises for you:\n{chr(10).join(['- ' + name for name in exercise_names])}"
                    except Exception as e:
                        print(f"Error getting exercise names: {e}")
                        exercise_suggestions = ""
                
                # Use user profile info
                profile_context = ""
                if user_profile:
                    if user_profile.workout_days_per_week:
                        profile_context += f"Since you work out {user_profile.workout_days_per_week} days per week, "
                    if user_profile.preferred_workout_time:
                        profile_context += f"and prefer {user_profile.preferred_workout_time} workouts, "
                    if user_profile.training_level:
                        profile_context += f"with your {user_profile.training_level} level, "
                
                return f"Yes {user_name}! I can create a personalized workout plan for you. {profile_context}Please tell me:\n- What is your goal? (weight loss, muscle gain, general fitness)\n- What type of exercises do you prefer? (cardio, strength, combination)\n\nBased on your history, I can suggest a plan that aligns with your previous activities.{exercise_suggestions}"
            
            # Nutrition request
            elif any(word in message_lower for word in ['nutrition', 'diet', 'meal', 'food']):
                context_nutrition = ""
                if nutrition_summary:
                    context_nutrition = f"Based on your current plan which includes {', '.join(nutrition_summary[:3])}, "
                return f"{context_nutrition}I can create a 2-week or 4-week nutrition plan for you. Please tell me:\n- What is your goal? (weight loss, weight gain, weight maintenance)\n- Do you have any dietary restrictions?\n- Would you prefer a 2-week or 4-week plan?"
            
            # Exercise history
            elif any(word in message_lower for word in ['history', 'past', 'previous']):
                if exercise_summary:
                    return f"Based on your history, your recent exercises include: {', '.join(exercise_summary)}. I can provide better suggestions based on this information to continue your fitness journey."
                else:
                    return "You haven't recorded any exercises yet. I can help you get started with a workout plan!"
            
            # Injury/health
            elif any(word in message_lower for word in ['injury', 'pain', 'hurt', 'ache']):
                return "If you're experiencing an injury or pain, it's important to consult a doctor or physical therapist. I can provide general information about common sports injuries and prevention methods in the 'Injuries' section."
            
            # Profile-related questions
            elif any(word in message_lower for word in ['profile', 'my info', 'my profile', 'my information']):
                if missing_profile_fields:
                    missing_fields_en = {
                        'age': 'age',
                        'weight': 'weight',
                        'height': 'height',
                        'gender': 'gender',
                        'training_level': 'training level',
                        'fitness_goals': 'fitness goals',
                        'workout_days_per_week': 'workout days per week',
                        'preferred_workout_time': 'preferred workout time',
                        'injuries': 'injuries'
                    }
                    missing_list = [missing_fields_en.get(f, f) for f in missing_profile_fields if f in missing_fields_en]
                    
                    return f"Hello {user_name}! I see your profile is incomplete. For more personalized plans and accurate recommendations, please go to the 'Profile' tab and complete the following information:\n\n" + \
                           "\n".join([f"• {field}" for field in missing_list]) + \
                           "\n\nAfter completing your profile, I can create more accurate workout and nutrition plans for you!"
                else:
                    # Profile is complete
                    profile_summary = f"Your profile is complete! "
                    if user_profile:
                        if user_profile.age and user_profile.weight and user_profile.height:
                            bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
                            profile_summary += f"Your BMI: {bmi:.1f}. "
                        if user_profile.training_level:
                            profile_summary += f"Your level: {user_profile.training_level}. "
                    return f"{profile_summary}If you want to update your profile information, go to the 'Profile' tab and click the 'Edit' button."
            
            # Questions about specific profile fields
            elif any(word in message_lower for word in ['age', 'how old', 'my age']):
                if user_profile and user_profile.age:
                    return f"Your age in profile: {user_profile.age} years. If you want to change it, go to the 'Profile' tab."
                else:
                    return "You haven't entered your age in your profile yet. Please go to the 'Profile' tab and enter your age. This information helps me create more appropriate plans for you."
            
            elif any(word in message_lower for word in ['weight', 'my weight', 'how much do i weigh']):
                if user_profile and user_profile.weight:
                    return f"Your weight in profile: {user_profile.weight} kg. If you want to change it, go to the 'Profile' tab."
                else:
                    return "You haven't entered your weight in your profile yet. Please go to the 'Profile' tab and enter your weight. This information is essential for calorie calculations and creating a nutrition plan."
            
            elif any(word in message_lower for word in ['height', 'tall', 'how tall', 'my height']):
                if user_profile and user_profile.height:
                    return f"Your height in profile: {user_profile.height} cm. If you want to change it, go to the 'Profile' tab."
                else:
                    return "You haven't entered your height in your profile yet. Please go to the 'Profile' tab and enter your height. This information is essential for BMI calculation and creating an appropriate plan."
            
            elif any(word in message_lower for word in ['level', 'training level', 'beginner', 'advanced']):
                if user_profile and user_profile.training_level:
                    return f"Your training level in profile: {user_profile.training_level}. If you want to change it, go to the 'Profile' tab."
                else:
                    return "You haven't specified your training level in your profile yet. Please go to the 'Profile' tab and select your level (beginner, intermediate, or advanced). This helps me suggest appropriate exercises for you."
            
            elif any(word in message_lower for word in ['goals', 'fitness goals', 'my goals', 'what are my goals']):
                if user_profile:
                    goals = user_profile.get_fitness_goals()
                    if goals:
                        return f"Your fitness goals: {', '.join(goals)}. If you want to change them, go to the 'Profile' tab."
                    else:
                        return "You haven't specified your fitness goals in your profile yet. Please go to the 'Profile' tab and select your goals (e.g., weight loss, muscle gain, strength, endurance, or flexibility)."
                else:
                    return "Please first complete your profile in the 'Profile' tab and specify your fitness goals."
            
            # General help
            else:
                suggestions = []
                if missing_profile_fields:
                    suggestions.append("completing your profile for more personalized plans")
                if not exercises:
                    suggestions.append("starting a workout plan")
                if not nutrition_plans:
                    suggestions.append("creating a nutrition plan")
                suggestions.append("getting tips and suggestions")
                
                profile_note = ""
                if missing_profile_fields:
                    profile_note = "\n\n💡 Suggestion: For more accurate plans, first complete your profile in the 'Profile' tab."
                
                return f"I understand. I can help you with:\n- Completing your profile\n- Creating a personalized workout plan\n- Nutrition planning\n- Answering fitness-related questions\n- Reviewing your exercise history\n\nPlease provide more details about your question or choose one of the options above.{profile_note}"
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in generate_ai_response: {e}")
        print(error_trace)
        # Always return a response, even on error
        try:
            if language == 'fa':
                return f"سلام {user_name}! متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید یا سوال خود را به شکل دیگری مطرح کنید."
            else:
                return f"Hello {user_name}! Sorry, an error occurred. Please try again or rephrase your question."
        except:
            # Final fallback
            return "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید." if language == 'fa' else "Sorry, an error occurred. Please try again."

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/health', methods=['GET'])
def health_alias():
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/public/training-info', methods=['GET'])
def get_public_training_info():
    """Public endpoint: training levels and corrective movements (no auth). Used by landing page."""
    import json
    try:
        from models import Configuration
        config = db.session.query(Configuration).first()
    except Exception:
        config = None
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
    _default_injury = lambda: {
        'purposes_fa': '', 'purposes_en': '', 'allowed_movements': [], 'forbidden_movements': [],
        'important_notes_fa': '', 'important_notes_en': ''
    }
    default_injuries = {k: _default_injury() for k in ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle']}
    default_injuries['common_injury_note_fa'] = ''
    default_injuries['common_injury_note_en'] = ''
    if not config:
        return jsonify({
            'training_levels': default_training_levels,
            'injuries': default_injuries
        }), 200
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


@app.route('/api/site-settings', methods=['GET'])
def get_site_settings_public():
    """Public endpoint: get website contact and social info for footer (no auth)."""
    try:
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        if not row:
            return jsonify({
                'contact_email': '',
                'contact_phone': '',
                'address_fa': '',
                'address_en': '',
                'app_description_fa': '',
                'app_description_en': '',
                'instagram_url': '',
                'telegram_url': '',
                'whatsapp_url': '',
                'twitter_url': '',
                'facebook_url': '',
                'linkedin_url': '',
                'youtube_url': '',
                'copyright_text': ''
            }), 200
        return jsonify({
            'contact_email': row.contact_email or '',
            'contact_phone': row.contact_phone or '',
            'address_fa': row.address_fa or '',
            'address_en': row.address_en or '',
            'app_description_fa': row.app_description_fa or '',
            'app_description_en': row.app_description_en or '',
            'instagram_url': row.instagram_url or '',
            'telegram_url': row.telegram_url or '',
            'whatsapp_url': row.whatsapp_url or '',
            'twitter_url': row.twitter_url or '',
            'facebook_url': row.facebook_url or '',
            'linkedin_url': row.linkedin_url or '',
            'youtube_url': row.youtube_url or '',
            'copyright_text': row.copyright_text or ''
        }), 200
    except Exception as e:
        print(f"Error get_site_settings_public: {e}")
        return jsonify({
            'contact_email': '',
            'contact_phone': '',
            'address_fa': '',
            'address_en': '',
            'app_description_fa': '',
            'app_description_en': '',
            'instagram_url': '',
            'telegram_url': '',
            'whatsapp_url': '',
            'twitter_url': '',
            'facebook_url': '',
            'linkedin_url': '',
            'youtube_url': '',
            'copyright_text': ''
        }), 200


# Register blueprints
try:
    from api.workout_plan_api import workout_plan_bp
    app.register_blueprint(workout_plan_bp)
except ImportError:
    pass

try:
    from api.workout_log_api import workout_log_bp
    app.register_blueprint(workout_log_bp)
except ImportError:
    pass

try:
    from api.ai_coach_api import ai_coach_bp
    app.register_blueprint(ai_coach_bp)
except ImportError:
    pass

try:
    from api.ai_plan_api import ai_plan_bp
    app.register_blueprint(ai_plan_bp)
except ImportError:
    pass

try:
    from api.admin_api import admin_bp
    app.register_blueprint(admin_bp)
except ImportError:
    pass

try:
    from api.exercise_library_api import exercise_library_bp
    app.register_blueprint(exercise_library_bp)
except ImportError:
    pass
try:
    from api.member_api import member_bp
    app.register_blueprint(member_bp)
except ImportError:
    pass
try:
    from api.messages_api import messages_bp
    app.register_blueprint(messages_bp)
except ImportError:
    pass
try:
    from api.website_kb_api import website_kb_bp
    app.register_blueprint(website_kb_bp)
except ImportError:
    pass

@app.route('/api/training-programs', methods=['GET'])
@jwt_required()
def get_training_programs():
    """Get training programs for the current user. If member on trial with no program, AI creates a 1-week trial program."""
    try:
        from models import TrainingProgram, UserProfile, MemberWeeklyGoal
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)

        user = db.session.query(User).filter_by(id=user_id).first()
        language = user.language if user and user.language else 'fa'

        user_programs = db.session.query(TrainingProgram).filter_by(user_id=user_id).all()
        general_programs = db.session.query(TrainingProgram).filter(TrainingProgram.user_id.is_(None)).all()

        # 7-day trial: if member has no program and trial is active, generate AI 1-week program
        trial_ends_at = getattr(user, 'trial_ends_at', None)
        trial_active = (
            user
            and getattr(user, 'role', None) == 'member'
            and trial_ends_at
            and trial_ends_at > datetime.utcnow()
        )
        if (
            user
            and getattr(user, 'role', None) == 'member'
            and trial_ends_at
            and trial_ends_at > datetime.utcnow()
            and not user_programs
        ):
            profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
            parts = []
            if profile:
                if profile.age:
                    parts.append(f"age={profile.age}")
                if profile.gender:
                    parts.append(f"gender={profile.gender}")
                if profile.training_level:
                    parts.append(f"training_level={profile.training_level}")
                if profile.workout_days_per_week:
                    parts.append(f"workout_days_per_week={profile.workout_days_per_week}")
                if profile.get_fitness_goals():
                    parts.append("fitness_goals=" + ",".join(profile.get_fitness_goals()))
                if profile.get_injuries():
                    parts.append("injuries=" + ",".join(profile.get_injuries()))
                if profile.equipment_access:
                    parts.append(f"equipment_access={profile.equipment_access}")
                if profile.gym_access is not None:
                    parts.append(f"gym_access={profile.gym_access}")
            profile_summary = "; ".join(parts) if parts else "No profile yet; use beginner level, 3 days per week."
            from services.session_ai_service import generate_trial_week_program
            import json as _json
            sessions = generate_trial_week_program(profile_summary, language)
            if sessions:
                name_fa = "برنامه هفته آزمایشی"
                name_en = "Trial week program"
                trial_program = TrainingProgram(
                    user_id=user_id,
                    name_fa=name_fa,
                    name_en=name_en,
                    description_fa="برنامه یک هفته‌ای شخصی‌سازی شده برای دوره آزمایشی شما.",
                    description_en="Personalized 1-week program for your free trial.",
                    duration_weeks=1,
                    training_level=(profile.training_level if profile else None) or "beginner",
                    category="hybrid",
                    sessions=_json.dumps(sessions, ensure_ascii=False),
                )
                db.session.add(trial_program)
                db.session.flush()
                goal = MemberWeeklyGoal(
                    user_id=user_id,
                    training_program_id=trial_program.id,
                    week_number=1,
                    goal_title_fa="هفته ۱: انجام جلسات هفته آزمایشی",
                    goal_title_en="Week 1: Complete your trial week sessions",
                )
                db.session.add(goal)
                db.session.commit()
                user_programs = db.session.query(TrainingProgram).filter_by(user_id=user_id).all()

        # During active trial, show only the trial program (no general plans)
        if trial_active:
            general_programs = []
        # For members with their own program(s), hide general templates to avoid duplicates
        if user and getattr(user, 'role', None) == 'member' and user_programs:
            general_programs = []
        all_programs = user_programs + general_programs
        programs_data = [program.to_dict(language) for program in all_programs]

        print(f"[Training Programs API] User ID: {user_id}, Language: {language}")
        print(f"[Training Programs API] Found {len(all_programs)} programs: {len(user_programs)} user-specific, {len(general_programs)} general")
        return jsonify(programs_data), 200
    except Exception as e:
        import traceback
        print(f"Error getting training programs: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/upload-analysis', methods=['POST'])
@jwt_required()
def upload_progress_analysis():
    """Upload muscle/fat analysis file (PDF or image) for AI extraction"""
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({'error': 'Invalid token'}), 401
        user_id = int(user_id_str)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        progress_entry_id = request.form.get('progress_entry_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Allowed: PDF, PNG, JPG, JPEG, GIF'}), 400
        
        # Save file
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads', 'progress_analysis')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # TODO: Add AI extraction here - for now, just save the file
        # In the future, this would:
        # 1. Extract text/data from PDF or image using OCR/AI
        # 2. Parse muscle mass and body fat percentage
        # 3. Update the ProgressEntry with extracted data
        
        # If progress_entry_id provided, update it
        if progress_entry_id:
            try:
                from models_workout_log import ProgressEntry
                entry = db.session.query(ProgressEntry).filter_by(id=progress_entry_id, user_id=user_id).first()
                if entry:
                    # Store file path in form_notes for now (or create a new field)
                    # For now, we'll just note that analysis was uploaded
                    pass
            except Exception as e:
                print(f"Error updating progress entry: {e}")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully. Analysis will be processed.',
            'filename': filename
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error uploading analysis file: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Serve frontend (React build) in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Let API and upload routes be handled by their own handlers
    if path.startswith('api') or path.startswith('uploads'):
        return jsonify({'error': 'Not Found'}), 404

    if app.static_folder:
        asset_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(asset_path):
            return send_from_directory(app.static_folder, path)

        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')

    return jsonify({'error': 'Frontend not built'}), 404

if __name__ == '__main__':
    with app.app_context():
        # Ensure SiteSettings (and other models) are registered before create_all
        try:
            from models import SiteSettings  # noqa: F401
        except ImportError:
            pass
        db.create_all()
        # Import additional models to ensure tables are created
        try:
            from models_workout_log import WorkoutLog, ProgressEntry, WeeklyGoal, WorkoutReminder
        except ImportError:
            pass
    app.run(debug=True, port=5000)

