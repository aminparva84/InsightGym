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
            'image_url': self.image_url
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
        db.Index('idx_user_workout_date', 'user_id', 'workout_date'),
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

