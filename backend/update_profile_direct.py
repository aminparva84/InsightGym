"""
Update profile using direct SQL to avoid model conflicts
"""

import sqlite3
import os
import json
import sys
import codecs

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def update_profile():
    db_paths = [
        'instance/raha_fitness.db',
        'raha_fitness.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("[ERROR] Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find demo user
        cursor.execute("SELECT id FROM user WHERE username = ?", ('demo',))
        user = cursor.fetchone()
        
        if not user:
            print("[ERROR] Demo user not found")
            conn.close()
            return False
        
        user_id = user[0]
        print(f"[INFO] Found demo user ID: {user_id}")
        
        # Check if profile exists
        cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        # Prepare profile data
        profile_data = {
            'age': 25,
            'weight': 75.5,
            'height': 175.0,
            'gender': 'male',
            'training_level': 'intermediate',
            'fitness_goals': json.dumps(['weight_loss', 'muscle_gain'], ensure_ascii=False),
            'injuries': json.dumps([], ensure_ascii=False),
            'injury_details': '',
            'medical_conditions': json.dumps([], ensure_ascii=False),
            'medical_condition_details': '',
            'exercise_history_years': 3,
            'exercise_history_description': 'Regular gym workouts for 3 years',
            'equipment_access': json.dumps(['machine', 'dumbbells', 'barbell'], ensure_ascii=False),
            'gym_access': 1,  # SQLite uses 1 for True
            'home_equipment': json.dumps([], ensure_ascii=False),
            'preferred_workout_time': 'evening',
            'workout_days_per_week': 4,
            'preferred_intensity': 'medium'
        }
        
        if profile:
            # Update existing profile
            print("[INFO] Updating existing profile...")
            cursor.execute("""
                UPDATE user_profiles SET
                    age = ?, weight = ?, height = ?, gender = ?,
                    training_level = ?, fitness_goals = ?, injuries = ?,
                    injury_details = ?, medical_conditions = ?, medical_condition_details = ?,
                    exercise_history_years = ?, exercise_history_description = ?,
                    equipment_access = ?, gym_access = ?, home_equipment = ?,
                    preferred_workout_time = ?, workout_days_per_week = ?,
                    preferred_intensity = ?, updated_at = datetime('now')
                WHERE user_id = ?
            """, (
                profile_data['age'], profile_data['weight'], profile_data['height'],
                profile_data['gender'], profile_data['training_level'],
                profile_data['fitness_goals'], profile_data['injuries'],
                profile_data['injury_details'], profile_data['medical_conditions'],
                profile_data['medical_condition_details'],
                profile_data['exercise_history_years'],
                profile_data['exercise_history_description'],
                profile_data['equipment_access'], profile_data['gym_access'],
                profile_data['home_equipment'], profile_data['preferred_workout_time'],
                profile_data['workout_days_per_week'], profile_data['preferred_intensity'],
                user_id
            ))
        else:
            # Create new profile
            print("[INFO] Creating new profile...")
            cursor.execute("""
                INSERT INTO user_profiles (
                    user_id, age, weight, height, gender, training_level,
                    fitness_goals, injuries, injury_details, medical_conditions,
                    medical_condition_details, exercise_history_years,
                    exercise_history_description, equipment_access, gym_access,
                    home_equipment, preferred_workout_time, workout_days_per_week,
                    preferred_intensity, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                user_id, profile_data['age'], profile_data['weight'],
                profile_data['height'], profile_data['gender'],
                profile_data['training_level'], profile_data['fitness_goals'],
                profile_data['injuries'], profile_data['injury_details'],
                profile_data['medical_conditions'],
                profile_data['medical_condition_details'],
                profile_data['exercise_history_years'],
                profile_data['exercise_history_description'],
                profile_data['equipment_access'], profile_data['gym_access'],
                profile_data['home_equipment'], profile_data['preferred_workout_time'],
                profile_data['workout_days_per_week'], profile_data['preferred_intensity']
            ))
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("PROFILE UPDATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nProfile Details:")
        print(f"  Age: {profile_data['age']}")
        print(f"  Weight: {profile_data['weight']} kg")
        print(f"  Height: {profile_data['height']} cm")
        print(f"  Gender: {profile_data['gender']}")
        print(f"  Training Level: {profile_data['training_level']}")
        print(f"  Fitness Goals: {json.loads(profile_data['fitness_goals'])}")
        print(f"  Gym Access: {bool(profile_data['gym_access'])}")
        print(f"  Equipment: {json.loads(profile_data['equipment_access'])}")
        print(f"  Workout Days: {profile_data['workout_days_per_week']}")
        print(f"  Preferred Time: {profile_data['preferred_workout_time']}")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_profile()
    sys.exit(0 if success else 1)


