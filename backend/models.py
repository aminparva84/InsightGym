"""
Database Models for AlphaFit Platform
Supports Persian (Farsi) and English text with UTF-8 encoding
"""

from app import db
from datetime import datetime
import json

# Exercise Categories
EXERCISE_CATEGORY_BODYBUILDING_MACHINE = 'bodybuilding_machine'  # حرکات باشگاهی با دستگاه
EXERCISE_CATEGORY_FUNCTIONAL_HOME = 'functional_home'  # حرکات فانکشنال / بدون وسیله
EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE = 'hybrid_hiit_machine'  # حرکات ترکیبی

# Training Levels
TRAINING_LEVEL_BEGINNER = 'beginner'
TRAINING_LEVEL_INTERMEDIATE = 'intermediate'
TRAINING_LEVEL_ADVANCED = 'advanced'

# Gender Suitability
GENDER_MALE = 'male'
GENDER_FEMALE = 'female'
GENDER_BOTH = 'both'

# Intensity Levels
INTENSITY_LIGHT = 'light'
INTENSITY_MEDIUM = 'medium'
INTENSITY_HEAVY = 'heavy'


# User model is defined in app.py, not here, to avoid duplicate class names
# The User class in app.py uses __tablename__ = 'user' (singular)
# All relationships to User should reference 'user.id' not 'users.id'
# 
# If you need to import User, use: from app import User
# Do NOT import User from models


class UserProfile(db.Model):
    """User Profile with detailed fitness information"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Basic Information
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    gender = db.Column(db.String(20))  # 'male', 'female', 'other'
    account_type = db.Column(db.String(20))  # 'assistant', 'member', 'admin'
    
    # Body Measurements (in cm)
    chest_circumference = db.Column(db.Float)  # in cm
    waist_circumference = db.Column(db.Float)  # in cm
    abdomen_circumference = db.Column(db.Float)  # in cm
    arm_circumference = db.Column(db.Float)  # in cm
    hip_circumference = db.Column(db.Float)  # in cm
    thigh_circumference = db.Column(db.Float)  # in cm
    
    # Training Information
    training_level = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced'
    fitness_goals = db.Column(db.Text)  # JSON array: ["weight_loss", "muscle_gain", "endurance", etc.]
    
    # Health Information
    injuries = db.Column(db.Text)  # JSON array: ["knee", "shoulder", "lower_back", etc.]
    injury_details = db.Column(db.Text)  # Detailed description of injuries
    medical_conditions = db.Column(db.Text)  # JSON array: ["heart_disease", "high_blood_pressure", "pregnancy", etc.]
    medical_condition_details = db.Column(db.Text)  # Detailed description of medical conditions
    exercise_history_years = db.Column(db.Integer)  # Years of exercise experience
    exercise_history_description = db.Column(db.Text)  # Description of exercise history
    
    # Equipment Access
    equipment_access = db.Column(db.Text)  # JSON array: ["machine", "dumbbells", "barbell", "home", etc.]
    gym_access = db.Column(db.Boolean, default=False)
    home_equipment = db.Column(db.Text)  # JSON array of available home equipment
    
    # Preferences
    preferred_workout_time = db.Column(db.String(20))  # 'morning', 'afternoon', 'evening'
    workout_days_per_week = db.Column(db.Integer)  # 1-7
    preferred_intensity = db.Column(db.String(20))  # 'light', 'medium', 'heavy'
    
    # Trainer Professional Details (for assistants/trainers)
    certifications = db.Column(db.Text)  # Certifications like NASM-CPT, ACE-CPT, etc.
    qualifications = db.Column(db.Text)  # Educational qualifications
    years_of_experience = db.Column(db.Integer)  # Years of training experience
    specialization = db.Column(db.String(200))  # Specialization areas
    education = db.Column(db.String(200))  # Education background
    bio = db.Column(db.Text)  # Trainer bio/description
    
    # Profile Image
    profile_image = db.Column(db.String(255))  # Filename of profile image
    
    # Metadata
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_fitness_goals(self):
        """Parse fitness_goals JSON string to list"""
        if self.fitness_goals:
            try:
                return json.loads(self.fitness_goals)
            except:
                return []
        return []
    
    def set_fitness_goals(self, goals_list):
        """Set fitness_goals from list to JSON string"""
        self.fitness_goals = json.dumps(goals_list, ensure_ascii=False)
    
    def get_injuries(self):
        """Parse injuries JSON string to list"""
        if self.injuries:
            try:
                return json.loads(self.injuries)
            except:
                return []
        return []
    
    def set_injuries(self, injuries_list):
        """Set injuries from list to JSON string"""
        self.injuries = json.dumps(injuries_list, ensure_ascii=False)
    
    def get_equipment_access(self):
        """Parse equipment_access JSON string to list"""
        if self.equipment_access:
            try:
                return json.loads(self.equipment_access)
            except:
                return []
        return []
    
    def set_equipment_access(self, equipment_list):
        """Set equipment_access from list to JSON string"""
        self.equipment_access = json.dumps(equipment_list, ensure_ascii=False)
    
    def get_home_equipment(self):
        """Parse home_equipment JSON string to list"""
        if self.home_equipment:
            try:
                return json.loads(self.home_equipment)
            except:
                return []
        return []
    
    def set_home_equipment(self, equipment_list):
        """Set home_equipment from list to JSON string"""
        self.home_equipment = json.dumps(equipment_list, ensure_ascii=False)
    
    def get_medical_conditions(self):
        """Parse medical_conditions JSON string to list"""
        if self.medical_conditions:
            try:
                return json.loads(self.medical_conditions)
            except:
                return []
        return []
    
    def set_medical_conditions(self, conditions_list):
        """Set medical_conditions from list to JSON string"""
        self.medical_conditions = json.dumps(conditions_list, ensure_ascii=False)


class Exercise(db.Model):
    """Exercise Library - Comprehensive exercise database with Persian/English support"""
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Category
    category = db.Column(db.String(50), nullable=False)  # 'bodybuilding_machine', 'functional_home', 'hybrid_hiit_machine'
    
    # Names (Persian & English)
    name_fa = db.Column(db.String(200), nullable=False)  # نام فارسی
    name_en = db.Column(db.String(200), nullable=False)  # English name
    
    # Target Information
    target_muscle_fa = db.Column(db.String(200), nullable=False)  # عضله درگیر (Persian)
    target_muscle_en = db.Column(db.String(200), nullable=False)  # Target Muscle (English)
    
    # Level and Intensity
    level = db.Column(db.String(20), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    intensity = db.Column(db.String(20), nullable=False)  # 'light', 'medium', 'heavy'
    
    # Execution Details
    execution_tips_fa = db.Column(db.Text)  # نکات اجرا (Persian)
    execution_tips_en = db.Column(db.Text)  # Execution Tips (English)
    
    # Breathing Guide
    breathing_guide_fa = db.Column(db.Text)  # دم و بازدم (Persian)
    breathing_guide_en = db.Column(db.Text)  # Breathing Guide (English)
    
    # Suitability
    gender_suitability = db.Column(db.String(20), nullable=False)  # 'male', 'female', 'both'
    
    # Injury Contraindications (JSON array of injury types)
    injury_contraindications = db.Column(db.Text)  # ["knee", "shoulder", "lower_back", etc.]
    
    # Additional Information
    equipment_needed_fa = db.Column(db.String(200))  # تجهیزات مورد نیاز (Persian)
    equipment_needed_en = db.Column(db.String(200))  # Equipment Needed (English)
    
    video_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    
    # Trainer / movement info (video, voice, text notes - shown in member training plan)
    voice_url = db.Column(db.String(500))  # uploaded voice note for this movement
    trainer_notes_fa = db.Column(db.Text)   # trainer text note (Persian)
    trainer_notes_en = db.Column(db.Text)  # trainer text note (English)
    # When during the exercise to notify the note/voice: 1 = after set 1, 2 = after set 2, etc. Null = at start of movement
    note_notify_at_seconds = db.Column(db.Integer, nullable=True)
    # If True, after completing a set the member is asked questions (how was it? which muscle?) and gets AI feedback
    ask_post_set_questions = db.Column(db.Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercise_history = db.relationship('ExerciseHistory', backref='exercise', lazy=True)
    
    def get_injury_contraindications(self):
        """Parse injury_contraindications JSON string to list"""
        if self.injury_contraindications:
            try:
                return json.loads(self.injury_contraindications)
            except:
                return []
        return []
    
    def set_injury_contraindications(self, injuries_list):
        """Set injury_contraindications from list to JSON string"""
        self.injury_contraindications = json.dumps(injuries_list, ensure_ascii=False)
    
    def to_dict(self, language='fa'):
        """Convert exercise to dictionary based on language"""
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name_fa if language == 'fa' else self.name_en,
            'name_fa': self.name_fa,
            'name_en': self.name_en,
            'target_muscle': self.target_muscle_fa if language == 'fa' else self.target_muscle_en,
            'target_muscle_fa': self.target_muscle_fa,
            'target_muscle_en': self.target_muscle_en,
            'level': self.level,
            'intensity': self.intensity,
            'execution_tips': self.execution_tips_fa if language == 'fa' else self.execution_tips_en,
            'execution_tips_fa': self.execution_tips_fa,
            'execution_tips_en': self.execution_tips_en,
            'breathing_guide': self.breathing_guide_fa if language == 'fa' else self.breathing_guide_en,
            'breathing_guide_fa': self.breathing_guide_fa,
            'breathing_guide_en': self.breathing_guide_en,
            'gender_suitability': self.gender_suitability,
            'injury_contraindications': self.get_injury_contraindications(),
            'equipment_needed': self.equipment_needed_fa if language == 'fa' else self.equipment_needed_en,
            'equipment_needed_fa': self.equipment_needed_fa,
            'equipment_needed_en': self.equipment_needed_en,
            'video_url': self.video_url,
            'image_url': self.image_url,
            'voice_url': self.voice_url or '',
            'trainer_notes': self.trainer_notes_fa if language == 'fa' else self.trainer_notes_en,
            'trainer_notes_fa': self.trainer_notes_fa or '',
            'trainer_notes_en': self.trainer_notes_en or '',
            'note_notify_at_seconds': self.note_notify_at_seconds,
            'ask_post_set_questions': getattr(self, 'ask_post_set_questions', False),
        }


class ExerciseHistory(db.Model):
    """Exercise History - tracks user's completed exercises"""
    __tablename__ = 'exercise_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Changed from 'users.id' to 'user.id' to match app.py User table
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)  # Can be null if custom exercise
    
    # Exercise Details (can override exercise defaults or be custom)
    exercise_name_fa = db.Column(db.String(200))
    exercise_name_en = db.Column(db.String(200))
    category = db.Column(db.String(50))
    
    # Workout Details
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)  # in kg
    duration = db.Column(db.Integer)  # in minutes (for cardio/HIIT)
    distance = db.Column(db.Float)  # in km (for running, cycling, etc.)
    calories_burned = db.Column(db.Integer)
    
    # Notes
    notes_fa = db.Column(db.Text)
    notes_en = db.Column(db.Text)
    
    # Date
    workout_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_exercise_history_user_workout_date', 'user_id', 'workout_date'),
    )


# ChatHistory is defined in app.py, not here to avoid conflicts


class NutritionPlan(db.Model):
    """Nutrition Plans"""
    __tablename__ = 'nutrition_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Changed from 'users.id' to 'user.id' to match app.py User table
    plan_type = db.Column(db.String(20), nullable=False)  # '2week' or '4week'
    day = db.Column(db.Integer, nullable=False)
    meal_type = db.Column(db.String(50))  # breakfast, lunch, dinner, snack
    food_item = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    notes = db.Column(db.Text)


class Tip(db.Model):
    """Fitness Tips"""
    __tablename__ = 'tips'
    
    id = db.Column(db.Integer, primary_key=True)
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    content_fa = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Injury(db.Model):
    """Injury Information"""
    __tablename__ = 'injuries'
    
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


class TrainingProgram(db.Model):
    """Training Programs - Comprehensive workout programs with sessions"""
    __tablename__ = 'training_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null for general programs, set for user-specific
    
    # Program Information
    name_fa = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Program Details
    duration_weeks = db.Column(db.Integer, default=4)  # 4 weeks = 1 month
    training_level = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced'
    category = db.Column(db.String(50))  # 'bodybuilding', 'functional', 'hiit', 'hybrid'
    
    # Sessions (JSON array of session objects)
    sessions = db.Column(db.Text)  # JSON array with session details
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_sessions(self):
        """Parse sessions JSON string to list"""
        if self.sessions:
            try:
                return json.loads(self.sessions)
            except:
                return []
        return []
    
    def set_sessions(self, sessions_list):
        """Set sessions from list to JSON string"""
        self.sessions = json.dumps(sessions_list, ensure_ascii=False)
    
    def to_dict(self, language='fa'):
        """Convert program to dictionary based on language"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name_fa if language == 'fa' else self.name_en,
            'name_fa': self.name_fa,
            'name_en': self.name_en,
            'description': self.description_fa if language == 'fa' else self.description_en,
            'description_fa': self.description_fa,
            'description_en': self.description_en,
            'duration_weeks': self.duration_weeks,
            'training_level': self.training_level,
            'category': self.category,
            'sessions': self.get_sessions()
        }


class PurchaseOrder(db.Model):
    """Training program purchase order (no payment gateway yet)."""
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_id = db.Column(db.Integer, nullable=False)
    packages_json = db.Column(db.Text)  # JSON array of selected packages
    ems_form_json = db.Column(db.Text)  # JSON object for EMS form (optional)
    discount_code = db.Column(db.String(50))
    subtotal = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(30), default='pending_payment')  # pending_payment, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'program_id': self.program_id,
            'packages': json.loads(self.packages_json) if self.packages_json else [],
            'ems_form': json.loads(self.ems_form_json) if self.ems_form_json else {},
            'discount_code': self.discount_code,
            'subtotal': self.subtotal,
            'discount_amount': self.discount_amount,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
        }

class MemberWeeklyGoal(db.Model):
    """Weekly mini-goals for members on a training plan (e.g. 1 month = 4 weekly goals)"""
    __tablename__ = 'member_weekly_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_program_id = db.Column(db.Integer, db.ForeignKey('training_programs.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # 1..duration_weeks
    
    goal_title_fa = db.Column(db.String(200))
    goal_title_en = db.Column(db.String(200))
    goal_description_fa = db.Column(db.Text)
    goal_description_en = db.Column(db.Text)
    
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'training_program_id', 'week_number', name='uq_member_program_week'),
    )


class DailySteps(db.Model):
    """Daily step count per user - from device (mobile) or manual entry"""
    __tablename__ = 'daily_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # date only
    steps = db.Column(db.Integer, default=0, nullable=False)
    source = db.Column(db.String(20), default='manual')  # 'manual' or 'device'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_date_steps'),
    )


class BreakRequest(db.Model):
    """Member break request - notifies admin or assigned assistant"""
    __tablename__ = 'break_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # member who requested
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'seen', 'accepted', 'denied'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seen_at = db.Column(db.DateTime, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)
    response_message = db.Column(db.Text, nullable=True)  # optional note from admin/assistant when accepting or denying
    
    __table_args__ = (
        db.Index('idx_break_requests_status', 'status'),
    )


class MemberTrainingActionCompletion(db.Model):
    """Tracks which training actions (session+exercise) a member has completed (ticked)."""
    __tablename__ = 'member_training_action_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_program_id = db.Column(db.Integer, db.ForeignKey('training_programs.id'), nullable=False)
    session_index = db.Column(db.Integer, nullable=False)  # 0-based index in program.sessions
    exercise_index = db.Column(db.Integer, nullable=False)  # 0-based index in session.exercises
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'training_program_id', 'session_index', 'exercise_index', name='uq_member_action'),
        db.Index('idx_member_action_user_program', 'user_id', 'training_program_id'),
    )


class Notification(db.Model):
    """In-app notifications for members (e.g. trainer notes sent to member)."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title_fa = db.Column(db.String(300))
    title_en = db.Column(db.String(300))
    body_fa = db.Column(db.Text)
    body_en = db.Column(db.Text)
    type = db.Column(db.String(50), default='trainer_note')  # 'trainer_note', 'reminder', etc.
    link = db.Column(db.String(500))  # optional deep link (e.g. ?tab=training-program)
    voice_url = db.Column(db.String(500))  # optional voice note URL
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.Index('idx_notifications_user_read', 'user_id', 'read_at'),)


class TrainingActionNote(db.Model):
    """Admin/trainer notes or voice notes per training action (program + session + exercise)."""
    __tablename__ = 'training_action_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    training_program_id = db.Column(db.Integer, db.ForeignKey('training_programs.id'), nullable=False)
    session_index = db.Column(db.Integer, nullable=False)
    exercise_index = db.Column(db.Integer, nullable=False)
    note_fa = db.Column(db.Text)
    note_en = db.Column(db.Text)
    voice_url = db.Column(db.String(500))  # URL or path to uploaded voice note
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # admin who added
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('training_program_id', 'session_index', 'exercise_index', name='uq_action_note'),
    )


class Configuration(db.Model):
    """Configuration for training levels and injuries"""
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    training_levels = db.Column(db.Text)  # JSON string
    injuries = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SiteSettings(db.Model):
    """Website info editable by admin: contact, social links, etc. Single row (singleton)."""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(100))
    address_fa = db.Column(db.String(500))
    address_en = db.Column(db.String(500))
    app_description_fa = db.Column(db.String(500))
    app_description_en = db.Column(db.String(500))
    instagram_url = db.Column(db.String(500))
    telegram_url = db.Column(db.String(500))
    whatsapp_url = db.Column(db.String(500))
    twitter_url = db.Column(db.String(500))
    facebook_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    copyright_text = db.Column(db.String(255))
    # JSON: session phases (warming, cooldown, ending message) with sub-steps for member session view
    session_phases_json = db.Column(db.Text)
    # JSON: buyable training plans and packages (names, descriptions, features, prices) for admin edit
    training_plans_products_json = db.Column(db.Text)
    # JSON: AI provider settings (selected_provider, openai/anthropic/gemini: api_key, source, last_tested_at, is_valid)
    ai_settings_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebsiteKBSource(db.Model):
    """Website KB raw source content. Single row (singleton)."""
    __tablename__ = 'website_kb_source'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebsiteKBChunk(db.Model):
    """Website KB chunks with embeddings for vector search. Uses local sentence-transformers (no API key)."""
    __tablename__ = 'website_kb_chunks'

    id = db.Column(db.Integer, primary_key=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=False)  # JSON array of floats
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProgressCheckRequest(db.Model):
    """Member requests a progress check; trainer can accept or deny."""
    __tablename__ = 'progress_check_requests'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, denied
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    responded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

