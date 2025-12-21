"""
Additional models for Workout Log and Progress Tracking
"""

from app import db
from datetime import datetime
import json

class WorkoutLog(db.Model):
    """User workout log entries"""
    __tablename__ = 'workout_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)
    exercise_name_fa = db.Column(db.String(200))  # For custom exercises
    exercise_name_en = db.Column(db.String(200))
    
    # Workout details
    sets_completed = db.Column(db.Integer, nullable=False)
    reps_completed = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float)  # Weight used
    duration_minutes = db.Column(db.Integer)  # For cardio/HIIT
    distance_km = db.Column(db.Float)  # For running/cycling
    
    # Feedback
    difficulty_rating = db.Column(db.String(20))  # 'too_easy', 'just_right', 'too_difficult'
    pain_reported = db.Column(db.Boolean, default=False)
    pain_location = db.Column(db.String(200))  # Where pain occurred
    form_rating = db.Column(db.Integer)  # 1-5 scale
    notes_fa = db.Column(db.Text)
    notes_en = db.Column(db.Text)
    
    # Alternative exercise (if suggested)
    alternative_exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)
    alternative_reason_fa = db.Column(db.String(200))
    alternative_reason_en = db.Column(db.String(200))
    
    # Timestamps
    workout_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='workout_logs')
    exercise = db.relationship('Exercise', foreign_keys=[exercise_id], backref='workout_logs')
    alternative_exercise = db.relationship('Exercise', foreign_keys=[alternative_exercise_id])
    
    __table_args__ = (
        db.Index('idx_user_workout_date', 'user_id', 'workout_date'),
    )

class ProgressEntry(db.Model):
    """User progress tracking (weight, measurements, form level)"""
    __tablename__ = 'progress_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Weight tracking
    weight_kg = db.Column(db.Float)
    
    # Body measurements (in cm)
    chest_cm = db.Column(db.Float)
    waist_cm = db.Column(db.Float)
    hips_cm = db.Column(db.Float)
    arm_left_cm = db.Column(db.Float)
    arm_right_cm = db.Column(db.Float)
    thigh_left_cm = db.Column(db.Float)
    thigh_right_cm = db.Column(db.Float)
    
    # Form level (overall assessment)
    form_level = db.Column(db.Integer)  # 1-5 scale
    form_notes_fa = db.Column(db.Text)
    form_notes_en = db.Column(db.Text)
    
    # Additional metrics
    body_fat_percentage = db.Column(db.Float)
    muscle_mass_kg = db.Column(db.Float)
    
    # Timestamp
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='progress_entries')
    
    __table_args__ = (
        db.Index('idx_user_recorded_at', 'user_id', 'recorded_at'),
    )

class WeeklyGoal(db.Model):
    """Weekly fitness goals"""
    __tablename__ = 'weekly_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Goal details
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    
    # Goal types and targets
    workout_days_target = db.Column(db.Integer)  # Target number of workout days
    workout_days_completed = db.Column(db.Integer, default=0)
    
    # Exercise-specific goals (JSON)
    exercise_goals = db.Column(db.Text)  # JSON: [{"exercise_id": 1, "sets": 3, "reps": 10}]
    
    # Weight/measurement goals
    target_weight_kg = db.Column(db.Float)
    target_measurements = db.Column(db.Text)  # JSON
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'failed'
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Notes
    notes_fa = db.Column(db.Text)
    notes_en = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='weekly_goals')
    
    def get_exercise_goals(self):
        """Parse exercise_goals JSON"""
        if self.exercise_goals:
            try:
                return json.loads(self.exercise_goals)
            except:
                return []
        return []
    
    def set_exercise_goals(self, goals_list):
        """Set exercise_goals from list"""
        self.exercise_goals = json.dumps(goals_list, ensure_ascii=False)
    
    def get_target_measurements(self):
        """Parse target_measurements JSON"""
        if self.target_measurements:
            try:
                return json.loads(self.target_measurements)
            except:
                return {}
        return {}
    
    def set_target_measurements(self, measurements_dict):
        """Set target_measurements from dict"""
        self.target_measurements = json.dumps(measurements_dict, ensure_ascii=False)

class WorkoutReminder(db.Model):
    """Daily workout reminders"""
    __tablename__ = 'workout_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Reminder settings
    enabled = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.Time, nullable=False)  # e.g., 18:00
    days_of_week = db.Column(db.String(20))  # JSON array: [1,2,3,4,5] for Mon-Fri
    timezone = db.Column(db.String(50), default='Asia/Tehran')
    
    # Reminder content
    message_fa = db.Column(db.Text)
    message_en = db.Column(db.Text)
    
    # Last sent
    last_sent_at = db.Column(db.DateTime)
    next_send_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='workout_reminders')
    
    def get_days_of_week(self):
        """Parse days_of_week JSON"""
        if self.days_of_week:
            try:
                return json.loads(self.days_of_week)
            except:
                return []
        return []
    
    def set_days_of_week(self, days_list):
        """Set days_of_week from list"""
        self.days_of_week = json.dumps(days_list, ensure_ascii=False)

