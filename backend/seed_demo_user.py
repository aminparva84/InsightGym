"""
Seed script to create demo user with random profile data
Run this to create a demo user for testing
"""

from app import app, db
from models import User, UserProfile, ExerciseHistory
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json
import random

def seed_demo_user():
    """Create demo user with random profile data"""
    
    # Check if demo user already exists
    demo_user = User.query.filter_by(username='demo').first()
    if demo_user:
        print("Demo user already exists. Deleting and recreating...")
        db.session.delete(demo_user)
        db.session.commit()
    
    # Create demo user
    demo_user = User(
        username='demo',
        email='demo@raha-fitness.com',
        password_hash=generate_password_hash('demo123'),
        language='fa'
    )
    db.session.add(demo_user)
    db.session.flush()
    
    print(f"✓ Created demo user: {demo_user.username} (ID: {demo_user.id})")
    
    # Random profile data
    genders = ['male', 'female']
    training_levels = ['beginner', 'intermediate', 'advanced']
    workout_times = ['morning', 'afternoon', 'evening']
    intensities = ['light', 'medium', 'heavy']
    fitness_goals_options = [
        ['weight_loss', 'endurance'],
        ['muscle_gain', 'strength'],
        ['weight_loss', 'muscle_gain'],
        ['endurance', 'flexibility'],
        ['muscle_gain', 'strength', 'endurance']
    ]
    injury_options = [
        [],
        ['knee'],
        ['shoulder'],
        ['lower_back'],
        ['knee', 'shoulder']
    ]
    equipment_options = [
        ['machine', 'dumbbells', 'barbell'],
        ['dumbbells', 'resistance_bands'],
        ['machine'],
        ['home']
    ]
    
    # Random selections
    gender = random.choice(genders)
    age = random.randint(20, 50)
    weight = round(random.uniform(55, 100), 1)
    height = round(random.uniform(160, 190), 1)
    training_level = random.choice(training_levels)
    fitness_goals = random.choice(fitness_goals_options)
    injuries = random.choice(injury_options)
    equipment_access = random.choice(equipment_options)
    gym_access = 'machine' in equipment_access
    workout_time = random.choice(workout_times)
    workout_days = random.randint(3, 6)
    intensity = random.choice(intensities)
    exercise_history_years = random.randint(0, 10)
    
    # Create user profile
    profile = UserProfile(
        user_id=demo_user.id,
        age=age,
        weight=weight,
        height=height,
        gender=gender,
        training_level=training_level,
        exercise_history_years=exercise_history_years,
        exercise_history_description=f"Started fitness journey {exercise_history_years} years ago. Focus on {', '.join(fitness_goals)}.",
        gym_access=gym_access,
        workout_days_per_week=workout_days,
        preferred_workout_time=workout_time,
        preferred_intensity=intensity,
        updated_at=datetime.utcnow()
    )
    
    # Set JSON fields
    profile.set_fitness_goals(fitness_goals)
    profile.set_injuries(injuries)
    profile.set_equipment_access(equipment_access)
    
    if injuries:
        injury_details_map = {
            'knee': 'مشکل جزئی در زانو، نیاز به احتیاط در تمرینات پا',
            'shoulder': 'درد خفیف در شانه، اجتناب از حرکات بالای سر',
            'lower_back': 'کمر درد خفیف، تمرکز بر حرکات ایمن'
        }
        profile.injury_details = ' '.join([injury_details_map.get(inj, '') for inj in injuries if inj in injury_details_map])
    
    if gym_access:
        profile.set_home_equipment(['dumbbells', 'resistance_bands'])
    else:
        profile.set_home_equipment(['resistance_bands', 'yoga_mat'])
    
    db.session.add(profile)
    print("✓ Created user profile with random data")
    print(f"  - Age: {age}, Gender: {gender}, Weight: {weight}kg, Height: {height}cm")
    print(f"  - Training Level: {training_level}, Goals: {', '.join(fitness_goals)}")
    print(f"  - Injuries: {', '.join(injuries) if injuries else 'None'}")
    print(f"  - Gym Access: {gym_access}, Workout Days: {workout_days}/week")
    
    # Create some sample exercise history
    exercise_names = [
        'اسکات', 'شنا سوئدی', 'پلانک', 'لانژ', 'برپی',
        'Squats', 'Push-ups', 'Plank', 'Lunges', 'Burpees'
    ]
    
    for i in range(10):
        days_ago = random.randint(0, 30)
        exercise_date = datetime.utcnow() - timedelta(days=days_ago)
        exercise = ExerciseHistory(
            user_id=demo_user.id,
            exercise_name_fa=random.choice(exercise_names),
            exercise_name_en=random.choice(exercise_names),
            category='functional_home',
            sets=random.randint(2, 4),
            reps=random.randint(8, 15),
            duration=random.randint(20, 60),
            calories_burned=random.randint(100, 400),
            workout_date=exercise_date,
            created_at=exercise_date
        )
        db.session.add(exercise)
    
    print("✓ Created sample exercise history")
    
    db.session.commit()
    print("\n" + "="*50)
    print("Demo user created successfully!")
    print("Username: demo")
    print("Password: demo123")
    print("="*50)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_demo_user()

