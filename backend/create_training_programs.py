"""
Script to create 4 comprehensive training programs (1 month each)
and assign one to complete_user_igl9lm
"""

from app import app, db
from models import TrainingProgram
from datetime import datetime
import json

def create_training_programs():
    with app.app_context():
        # Create tables if they don't exist
        from models import TrainingProgram
        db.create_all()
        print("Database tables created/verified")
        
        # Create 4 training programs
        
        # Program 1: Beginner Full Body (1 Month)
        program1_sessions = [
            {
                "week": 1,
                "day": 1,
                "name_fa": "تمرین کامل بدن - روز اول",
                "name_en": "Full Body Workout - Day 1",
                "exercises": [
                    {
                        "name_fa": "اسکوات",
                        "name_en": "Squats",
                        "sets": 3,
                        "reps": "10-12",
                        "rest": "60 seconds",
                        "instructions_fa": "پاها را به عرض شانه باز کنید. به آرامی پایین بروید تا ران‌ها موازی زمین شوند. سپس به حالت اولیه برگردید.",
                        "instructions_en": "Stand with feet shoulder-width apart. Lower down until thighs are parallel to the floor. Return to starting position."
                    },
                    {
                        "name_fa": "پرس سینه",
                        "name_en": "Chest Press",
                        "sets": 3,
                        "reps": "10-12",
                        "rest": "60 seconds",
                        "instructions_fa": "روی نیمکت دراز بکشید. هالتر را به آرامی پایین بیاورید و سپس به بالا فشار دهید.",
                        "instructions_en": "Lie on bench. Lower the bar slowly and press up."
                    },
                    {
                        "name_fa": "زیر بغل",
                        "name_en": "Lat Pulldown",
                        "sets": 3,
                        "reps": "10-12",
                        "rest": "60 seconds",
                        "instructions_fa": "نشسته، میله را به سمت قفسه سینه بکشید. به آرامی رها کنید.",
                        "instructions_en": "Seated, pull the bar to your chest. Slowly release."
                    }
                ]
            },
            {
                "week": 1,
                "day": 2,
                "name_fa": "تمرین کامل بدن - روز دوم",
                "name_en": "Full Body Workout - Day 2",
                "exercises": [
                    {
                        "name_fa": "لانژ",
                        "name_en": "Lunges",
                        "sets": 3,
                        "reps": "10 each leg",
                        "rest": "60 seconds",
                        "instructions_fa": "یک پا را به جلو بگذارید و پایین بروید. به حالت اولیه برگردید و با پای دیگر تکرار کنید.",
                        "instructions_en": "Step one foot forward and lower down. Return and repeat with other leg."
                    },
                    {
                        "name_fa": "پرس شانه",
                        "name_en": "Shoulder Press",
                        "sets": 3,
                        "reps": "10-12",
                        "rest": "60 seconds",
                        "instructions_fa": "دمبل‌ها را به بالای سر فشار دهید. به آرامی پایین بیاورید.",
                        "instructions_en": "Press dumbbells overhead. Slowly lower down."
                    },
                    {
                        "name_fa": "پلانک",
                        "name_en": "Plank",
                        "sets": 3,
                        "reps": "30-45 seconds",
                        "rest": "60 seconds",
                        "instructions_fa": "در حالت شنا قرار بگیرید. بدن را صاف نگه دارید.",
                        "instructions_en": "Get into push-up position. Keep body straight."
                    }
                ]
            }
        ]
        
        # Add more sessions for weeks 2-4 (simplified for brevity, but should have all 4 weeks)
        for week in range(2, 5):
            for day in range(1, 4):  # 3 days per week
                program1_sessions.append({
                    "week": week,
                    "day": day,
                    "name_fa": f"تمرین کامل بدن - هفته {week} روز {day}",
                    "name_en": f"Full Body Workout - Week {week} Day {day}",
                    "exercises": [
                        {
                            "name_fa": "اسکوات",
                            "name_en": "Squats",
                            "sets": 3,
                            "reps": "12-15" if week > 2 else "10-12",
                            "rest": "60 seconds",
                            "instructions_fa": "پاها را به عرض شانه باز کنید. به آرامی پایین بروید.",
                            "instructions_en": "Stand with feet shoulder-width apart. Lower down slowly."
                        },
                        {
                            "name_fa": "پرس سینه",
                            "name_en": "Chest Press",
                            "sets": 3,
                            "reps": "12-15" if week > 2 else "10-12",
                            "rest": "60 seconds",
                            "instructions_fa": "روی نیمکت دراز بکشید و هالتر را فشار دهید.",
                            "instructions_en": "Lie on bench and press the bar."
                        }
                    ]
                })
        
        program1 = TrainingProgram(
            name_fa="برنامه کامل بدن برای مبتدیان",
            name_en="Beginner Full Body Program",
            description_fa="برنامه 4 هفته‌ای برای مبتدیان که تمام عضلات بدن را در بر می‌گیرد. مناسب برای شروع تمرینات.",
            description_en="4-week program for beginners covering all muscle groups. Perfect for starting your fitness journey.",
            duration_weeks=4,
            training_level="beginner",
            category="bodybuilding",
            sessions=json.dumps(program1_sessions, ensure_ascii=False)
        )
        
        # Program 2: Intermediate Split (1 Month)
        program2_sessions = []
        for week in range(1, 5):
            program2_sessions.extend([
                {
                    "week": week,
                    "day": 1,
                    "name_fa": f"سینه و پشت بازو - هفته {week}",
                    "name_en": f"Chest & Triceps - Week {week}",
                    "exercises": [
                        {"name_fa": "پرس سینه", "name_en": "Bench Press", "sets": 4, "reps": "8-10", "rest": "90 seconds", "instructions_fa": "پرس سینه با هالتر", "instructions_en": "Bench press with barbell"},
                        {"name_fa": "پرس سینه دمبل", "name_en": "Dumbbell Press", "sets": 3, "reps": "10-12", "rest": "90 seconds", "instructions_fa": "پرس سینه با دمبل", "instructions_en": "Dumbbell chest press"},
                        {"name_fa": "پشت بازو", "name_en": "Tricep Extension", "sets": 3, "reps": "12-15", "rest": "60 seconds", "instructions_fa": "تمرین پشت بازو", "instructions_en": "Tricep exercise"}
                    ]
                },
                {
                    "week": week,
                    "day": 2,
                    "name_fa": f"پشت و جلو بازو - هفته {week}",
                    "name_en": f"Back & Biceps - Week {week}",
                    "exercises": [
                        {"name_fa": "زیر بغل", "name_en": "Lat Pulldown", "sets": 4, "reps": "8-10", "rest": "90 seconds", "instructions_fa": "زیر بغل با دستگاه", "instructions_en": "Lat pulldown machine"},
                        {"name_fa": "جلو بازو", "name_en": "Bicep Curl", "sets": 3, "reps": "12-15", "rest": "60 seconds", "instructions_fa": "جلو بازو با دمبل", "instructions_en": "Dumbbell bicep curl"}
                    ]
                },
                {
                    "week": week,
                    "day": 3,
                    "name_fa": f"پا و شانه - هفته {week}",
                    "name_en": f"Legs & Shoulders - Week {week}",
                    "exercises": [
                        {"name_fa": "اسکوات", "name_en": "Squats", "sets": 4, "reps": "8-10", "rest": "90 seconds", "instructions_fa": "اسکوات با هالتر", "instructions_en": "Barbell squats"},
                        {"name_fa": "پرس شانه", "name_en": "Shoulder Press", "sets": 3, "reps": "10-12", "rest": "90 seconds", "instructions_fa": "پرس شانه", "instructions_en": "Shoulder press"}
                    ]
                }
            ])
        
        program2 = TrainingProgram(
            name_fa="برنامه تقسیم عضلات متوسط",
            name_en="Intermediate Split Program",
            description_fa="برنامه 4 هفته‌ای با تقسیم عضلات برای افراد با تجربه متوسط. تمرینات 3 روز در هفته.",
            description_en="4-week split program for intermediate trainees. 3 days per week training.",
            duration_weeks=4,
            training_level="intermediate",
            category="bodybuilding",
            sessions=json.dumps(program2_sessions, ensure_ascii=False)
        )
        
        # Program 3: Advanced Push/Pull/Legs (1 Month)
        program3_sessions = []
        for week in range(1, 5):
            program3_sessions.extend([
                {
                    "week": week,
                    "day": 1,
                    "name_fa": f"Push Day - هفته {week}",
                    "name_en": f"Push Day - Week {week}",
                    "exercises": [
                        {"name_fa": "پرس سینه", "name_en": "Bench Press", "sets": 5, "reps": "5-6", "rest": "3 minutes", "instructions_fa": "پرس سینه سنگین", "instructions_en": "Heavy bench press"},
                        {"name_fa": "پرس شانه", "name_en": "Overhead Press", "sets": 4, "reps": "6-8", "rest": "2 minutes", "instructions_fa": "پرس شانه ایستاده", "instructions_en": "Standing overhead press"},
                        {"name_fa": "پشت بازو", "name_en": "Close Grip Bench", "sets": 3, "reps": "8-10", "rest": "90 seconds", "instructions_fa": "پرس سینه دست جمع", "instructions_en": "Close grip bench press"}
                    ]
                },
                {
                    "week": week,
                    "day": 2,
                    "name_fa": f"Pull Day - هفته {week}",
                    "name_en": f"Pull Day - Week {week}",
                    "exercises": [
                        {"name_fa": "ددلیفت", "name_en": "Deadlift", "sets": 5, "reps": "5", "rest": "3 minutes", "instructions_fa": "ددلیفت کلاسیک", "instructions_en": "Classic deadlift"},
                        {"name_fa": "زیر بغل", "name_en": "Pull-ups", "sets": 4, "reps": "8-10", "rest": "2 minutes", "instructions_fa": "بارفیکس", "instructions_en": "Pull-ups"},
                        {"name_fa": "جلو بازو", "name_en": "Barbell Curl", "sets": 3, "reps": "8-10", "rest": "90 seconds", "instructions_fa": "جلو بازو با هالتر", "instructions_en": "Barbell curl"}
                    ]
                },
                {
                    "week": week,
                    "day": 3,
                    "name_fa": f"Leg Day - هفته {week}",
                    "name_en": f"Leg Day - Week {week}",
                    "exercises": [
                        {"name_fa": "اسکوات", "name_en": "Squats", "sets": 5, "reps": "5-6", "rest": "3 minutes", "instructions_fa": "اسکوات سنگین", "instructions_en": "Heavy squats"},
                        {"name_fa": "پرس پا", "name_en": "Leg Press", "sets": 4, "reps": "10-12", "rest": "2 minutes", "instructions_fa": "پرس پا با دستگاه", "instructions_en": "Leg press machine"},
                        {"name_fa": "لانژ", "name_en": "Walking Lunges", "sets": 3, "reps": "12 each leg", "rest": "90 seconds", "instructions_fa": "لانژ راه رونده", "instructions_en": "Walking lunges"}
                    ]
                }
            ])
        
        program3 = TrainingProgram(
            name_fa="برنامه پیشرفته Push/Pull/Legs",
            name_en="Advanced Push/Pull/Legs Program",
            description_fa="برنامه 4 هفته‌ای پیشرفته با تقسیم Push/Pull/Legs. مناسب برای افراد با تجربه بالا.",
            description_en="4-week advanced program with Push/Pull/Legs split. For experienced trainees.",
            duration_weeks=4,
            training_level="advanced",
            category="bodybuilding",
            sessions=json.dumps(program3_sessions, ensure_ascii=False)
        )
        
        # Program 4: Functional HIIT (1 Month)
        program4_sessions = []
        for week in range(1, 5):
            program4_sessions.extend([
                {
                    "week": week,
                    "day": 1,
                    "name_fa": f"HIIT کامل بدن - هفته {week}",
                    "name_en": f"Full Body HIIT - Week {week}",
                    "exercises": [
                        {"name_fa": "برپی", "name_en": "Burpees", "sets": 4, "reps": "30 seconds", "rest": "30 seconds", "instructions_fa": "برپی کامل با پرش", "instructions_en": "Full burpee with jump"},
                        {"name_fa": "کوهنورد", "name_en": "Mountain Climbers", "sets": 4, "reps": "30 seconds", "rest": "30 seconds", "instructions_fa": "کوهنورد سریع", "instructions_en": "Fast mountain climbers"},
                        {"name_fa": "پرش اسکوات", "name_en": "Jump Squats", "sets": 4, "reps": "20", "rest": "30 seconds", "instructions_fa": "اسکوات با پرش", "instructions_en": "Squat jumps"}
                    ]
                },
                {
                    "week": week,
                    "day": 2,
                    "name_fa": f"تمرین قدرتی - هفته {week}",
                    "name_en": f"Strength Training - Week {week}",
                    "exercises": [
                        {"name_fa": "اسکوات", "name_en": "Goblet Squats", "sets": 4, "reps": "15", "rest": "60 seconds", "instructions_fa": "اسکوات با دمبل", "instructions_en": "Dumbbell goblet squats"},
                        {"name_fa": "پرس شانه", "name_en": "Push Press", "sets": 3, "reps": "12", "rest": "60 seconds", "instructions_fa": "پرس شانه انفجاری", "instructions_en": "Explosive push press"}
                    ]
                },
                {
                    "week": week,
                    "day": 3,
                    "name_fa": f"کاردیو - هفته {week}",
                    "name_en": f"Cardio - Week {week}",
                    "exercises": [
                        {"name_fa": "دویدن", "name_en": "Running", "sets": 1, "reps": "20 minutes", "rest": "0", "instructions_fa": "دویدن با سرعت متوسط", "instructions_en": "Moderate pace running"},
                        {"name_fa": "طناب زدن", "name_en": "Jump Rope", "sets": 5, "reps": "1 minute", "rest": "30 seconds", "instructions_fa": "طناب زدن سریع", "instructions_en": "Fast jump rope"}
                    ]
                }
            ])
        
        program4 = TrainingProgram(
            name_fa="برنامه فانکشنال HIIT",
            name_en="Functional HIIT Program",
            description_fa="برنامه 4 هفته‌ای فانکشنال با تمرینات HIIT. مناسب برای بهبود استقامت و قدرت.",
            description_en="4-week functional program with HIIT training. Great for endurance and strength.",
            duration_weeks=4,
            training_level="intermediate",
            category="functional",
            sessions=json.dumps(program4_sessions, ensure_ascii=False)
        )
        
        # Add programs to database
        db.session.add(program1)
        db.session.add(program2)
        db.session.add(program3)
        db.session.add(program4)
        db.session.commit()
        
        print("Created 4 training programs:")
        print(f"1. {program1.name_en} (ID: {program1.id})")
        print(f"2. {program2.name_en} (ID: {program2.id})")
        print(f"3. {program3.name_en} (ID: {program3.id})")
        print(f"4. {program4.name_en} (ID: {program4.id})")
        
        # Assign program 2 to complete_user_igl9lm (user_id: 10)
        from app import User
        user = User.query.filter_by(username='complete_user_igl9lm').first()
        if user:
            user_program = TrainingProgram(
                name_fa=program2.name_fa,
                name_en=program2.name_en,
                description_fa=program2.description_fa,
                description_en=program2.description_en,
                duration_weeks=program2.duration_weeks,
                training_level=program2.training_level,
                category=program2.category,
                sessions=program2.sessions,
                user_id=user.id
            )
            db.session.add(user_program)
            db.session.commit()
            print(f"\nAssigned {program2.name_en} to user {user.username} (ID: {user.id})")
        else:
            print("\nUser 'complete_user_igl9lm' not found!")
        
        print("\nTraining programs created successfully!")

if __name__ == '__main__':
    create_training_programs()

