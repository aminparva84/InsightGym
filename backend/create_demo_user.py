"""
Create demo user for testing
Run this script to create a demo user with sample data
"""

from app import app, db
# Import User from app.py (old model)
from app import User, Exercise as OldExercise, ChatHistory, NutritionPlan, Tip, Injury
# Import new models
from models import UserProfile, Exercise, ExerciseHistory
from models_workout_log import WorkoutLog, ProgressEntry, WeeklyGoal, WorkoutReminder
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date, time
import json

def create_demo_user():
    """Create demo user with sample data"""
    
    with app.app_context():
        # Check if demo user already exists
        demo_user = User.query.filter_by(username='demo').first()
        if demo_user:
            print("Demo user already exists!")
            print(f"Username: demo")
            print(f"Password: demo123")
            print(f"Email: demo@raha-fitness.com")
            return
        
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@raha-fitness.com',
            password_hash=generate_password_hash('demo123'),
            language='fa',
            created_at=datetime.utcnow()
        )
        db.session.add(demo_user)
        db.session.flush()  # Get user ID
        
        print(f"✓ Created demo user: {demo_user.username} (ID: {demo_user.id})")
        
        # Create user profile
        profile = UserProfile(
            user_id=demo_user.id,
            age=30,
            weight=75.5,
            height=175.0,
            gender='male',
            training_level='intermediate',
            fitness_goals=json.dumps(['muscle_gain', 'strength'], ensure_ascii=False),
            injuries=json.dumps(['knee'], ensure_ascii=False),
            equipment_access=json.dumps(['machine', 'dumbbells'], ensure_ascii=False),
            gym_access=True,
            home_equipment=json.dumps(['dumbbells', 'resistance_bands'], ensure_ascii=False),
            preferred_workout_time='evening',
            workout_days_per_week=4,
            preferred_intensity='medium',
            updated_at=datetime.utcnow()
        )
        db.session.add(profile)
        print("✓ Created user profile")
        
        # Create sample exercises (if they exist)
        exercises = Exercise.query.limit(5).all()
        if exercises:
            # Create exercise history
            for i, exercise in enumerate(exercises):
                history = ExerciseHistory(
                    user_id=demo_user.id,
                    exercise_id=exercise.id,
                    sets=3,
                    reps=10,
                    weight=50.0,
                    workout_date=datetime.utcnow() - timedelta(days=i),
                    created_at=datetime.utcnow() - timedelta(days=i)
                )
                db.session.add(history)
            print(f"✓ Created {len(exercises)} exercise history entries")
            
            # Create workout logs
            for i, exercise in enumerate(exercises[:3]):
                log = WorkoutLog(
                    user_id=demo_user.id,
                    exercise_id=exercise.id,
                    exercise_name_fa=exercise.name_fa,
                    exercise_name_en=exercise.name_en,
                    sets_completed=3,
                    reps_completed=10,
                    weight_kg=50.0,
                    difficulty_rating='just_right',
                    form_rating=4,
                    workout_date=datetime.utcnow() - timedelta(days=i),
                    created_at=datetime.utcnow() - timedelta(days=i)
                )
                db.session.add(log)
            print("✓ Created workout logs")
        
        # Create chat history
        chat_entries = [
            {
                'message': 'سلام',
                'response': 'سلام! من دستیار هوشمند رها فیتنس هستم. چگونه می‌توانم به شما کمک کنم؟'
            },
            {
                'message': 'برنامه تمرینی می‌خواهم',
                'response': 'بله! می‌توانم یک برنامه تمرینی شخصی برای شما ایجاد کنم. لطفاً بگویید هدف شما چیست؟'
            }
        ]
        
        for entry in chat_entries:
            chat = ChatHistory(
                user_id=demo_user.id,
                message=entry['message'],
                response=entry['response'],
                timestamp=datetime.utcnow() - timedelta(days=len(chat_entries) - chat_entries.index(entry))
            )
            db.session.add(chat)
        print("✓ Created chat history")
        
        # Create nutrition plans
        for day in range(1, 8):  # One week
            meals = [
                {'type': 'breakfast', 'food': 'تخم مرغ و نان تست', 'calories': 350},
                {'type': 'lunch', 'food': 'مرغ و برنج', 'calories': 500},
                {'type': 'dinner', 'food': 'ماهی و سبزیجات', 'calories': 400}
            ]
            
            for meal in meals:
                plan = NutritionPlan(
                    user_id=demo_user.id,
                    plan_type='2week',
                    day=day,
                    meal_type=meal['type'],
                    food_item=meal['food'],
                    calories=meal['calories'],
                    protein=30.0,
                    carbs=40.0,
                    fats=15.0
                )
                db.session.add(plan)
        print("✓ Created nutrition plans")
        
        # Create progress entries
        base_weight = 75.5
        for i in range(4):  # 4 weeks of progress
            progress = ProgressEntry(
                user_id=demo_user.id,
                weight_kg=base_weight - (i * 0.5),  # Losing weight
                chest_cm=100 + (i * 1),  # Gaining muscle
                waist_cm=85 - (i * 0.5),
                form_level=3 + (i * 0.5),
                recorded_at=datetime.utcnow() - timedelta(weeks=4-i),
                created_at=datetime.utcnow() - timedelta(weeks=4-i)
            )
            db.session.add(progress)
        print("✓ Created progress entries")
        
        # Create weekly goal
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        goal = WeeklyGoal(
            user_id=demo_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            workout_days_target=4,
            workout_days_completed=2,
            status='active',
            completion_percentage=50.0,
            notes_fa='هدف این هفته: تمرین ۴ روز در هفته',
            notes_en='This week goal: 4 workout days'
        )
        db.session.add(goal)
        print("✓ Created weekly goal")
        
        # Create workout reminder
        reminder = WorkoutReminder(
            user_id=demo_user.id,
            enabled=True,
            reminder_time=time(18, 0),  # 6 PM
            days_of_week=json.dumps([1, 2, 3, 4, 5]),  # Mon-Fri
            message_fa='زمان تمرین شما فرا رسیده است! 💪',
            message_en='Time for your workout! 💪',
            timezone='Asia/Tehran',
            next_send_at=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        )
        db.session.add(reminder)
        print("✓ Created workout reminder")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*50)
        print("DEMO USER CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Username: demo")
        print(f"Password: demo123")
        print(f"Email: demo@raha-fitness.com")
        print(f"Language: Farsi (Persian)")
        print("\nYou can now log in to see the member landing page!")
        print("="*50)

if __name__ == '__main__':
    create_demo_user()

