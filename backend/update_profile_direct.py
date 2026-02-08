"""
Update profile using Flask app context and SQLAlchemy.
Works with PostgreSQL or SQLite via DATABASE_URL.
"""

import json
import os
import sys
import codecs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from app import app, db, User
from models import UserProfile

def update_profile():
    with app.app_context():
        try:
            user = User.query.filter_by(username='demo').first()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            return False
        if not user:
            print("[ERROR] Demo user not found")
            return False
        print(f"[INFO] Found demo user ID: {user.id}")
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            print("[INFO] Creating new profile...")
        else:
            print("[INFO] Updating existing profile...")
        profile.age = 25
        profile.weight = 75.5
        profile.height = 175.0
        profile.gender = 'male'
        profile.training_level = 'intermediate'
        profile.set_fitness_goals(['weight_loss', 'muscle_gain'])
        profile.set_injuries([])
        profile.injury_details = ''
        profile.medical_conditions = json.dumps([], ensure_ascii=False)
        profile.medical_condition_details = ''
        profile.exercise_history_years = 3
        profile.exercise_history_description = 'Regular gym workouts for 3 years'
        profile.set_equipment_access(['machine', 'dumbbells', 'barbell'])
        profile.gym_access = True
        profile.set_home_equipment([])
        profile.preferred_workout_time = 'evening'
        profile.workout_days_per_week = 4
        profile.preferred_intensity = 'medium'
        db.session.commit()
        print("\n" + "="*60)
        print("PROFILE UPDATED SUCCESSFULLY!")
        print("="*60)
        print("\nProfile Details:")
        print(f"  Age: {profile.age}")
        print(f"  Weight: {profile.weight} kg")
        print(f"  Height: {profile.height} cm")
        print(f"  Gender: {profile.gender}")
        print(f"  Training Level: {profile.training_level}")
        print(f"  Fitness Goals: {profile.get_fitness_goals()}")
        print(f"  Gym Access: {profile.gym_access}")
        print(f"  Equipment: {profile.get_equipment_access()}")
        print(f"  Workout Days: {profile.workout_days_per_week}")
        print(f"  Preferred Time: {profile.preferred_workout_time}")
        print("="*60)
        return True

if __name__ == '__main__':
    success = update_profile()
    sys.exit(0 if success else 1)
