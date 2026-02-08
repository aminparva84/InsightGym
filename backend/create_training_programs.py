"""
Script to create a single 4-week training program.
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
        
        # Create a single 4-week training program
        
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
        
        # Add program to database
        db.session.add(program1)
        db.session.commit()
        
        print("Created 1 training program:")
        print(f"1. {program1.name_en} (ID: {program1.id})")
        print("\nTraining program created successfully!")

if __name__ == '__main__':
    create_training_programs()

