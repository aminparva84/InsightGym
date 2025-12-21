"""
Seed script to populate exercise library with sample exercises
Run this after setting up the database to add sample exercises in all categories
"""

from app import app, db
from models import (
    Exercise, 
    EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
    EXERCISE_CATEGORY_FUNCTIONAL_HOME,
    EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE,
    TRAINING_LEVEL_BEGINNER,
    TRAINING_LEVEL_INTERMEDIATE,
    TRAINING_LEVEL_ADVANCED,
    INTENSITY_LIGHT,
    INTENSITY_MEDIUM,
    INTENSITY_HEAVY,
    GENDER_MALE,
    GENDER_FEMALE,
    GENDER_BOTH
)

def seed_exercises():
    """Add sample exercises in all three categories"""
    
    exercises = [
        # Bodybuilding - Machine Category
        {
            'category': EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
            'name_fa': 'پرس سینه با دستگاه',
            'name_en': 'Chest Press Machine',
            'target_muscle_fa': 'سینه، شانه، سه‌سر بازو',
            'target_muscle_en': 'Chest, Shoulders, Triceps',
            'level': TRAINING_LEVEL_INTERMEDIATE,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': 'کمر را صاف نگه دارید و به آرامی وزنه را پایین بیاورید. در نقطه پایین، ۱-۲ ثانیه مکث کنید.',
            'execution_tips_en': 'Keep your back straight and slowly lower the weight. Pause for 1-2 seconds at the bottom.',
            'breathing_guide_fa': 'دم هنگام پایین آوردن، بازدم هنگام بالا بردن',
            'breathing_guide_en': 'Inhale when lowering, exhale when pushing up',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["shoulder", "lower_back"]',
            'equipment_needed_fa': 'دستگاه پرس سینه',
            'equipment_needed_en': 'Chest Press Machine'
        },
        {
            'category': EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
            'name_fa': 'پرس پا',
            'name_en': 'Leg Press',
            'target_muscle_fa': 'چهارسر ران، باسن، همسترینگ',
            'target_muscle_en': 'Quadriceps, Glutes, Hamstrings',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': 'پاها را به عرض شانه باز کنید. زانوها را بیش از ۹۰ درجه خم نکنید.',
            'execution_tips_en': 'Place feet shoulder-width apart. Do not bend knees beyond 90 degrees.',
            'breathing_guide_fa': 'دم هنگام پایین آوردن، بازدم هنگام بالا بردن',
            'breathing_guide_en': 'Inhale when lowering, exhale when pushing up',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["knee", "lower_back"]',
            'equipment_needed_fa': 'دستگاه پرس پا',
            'equipment_needed_en': 'Leg Press Machine'
        },
        {
            'category': EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
            'name_fa': 'لت از جلو',
            'name_en': 'Lat Pulldown',
            'target_muscle_fa': 'پشت بازو، لاتیسموس، شانه',
            'target_muscle_en': 'Lats, Rhomboids, Shoulders',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': 'کمر را صاف نگه دارید. دسته را به سمت سینه پایین بیاورید، نه پشت گردن.',
            'execution_tips_en': 'Keep your back straight. Pull the bar toward your chest, not behind your neck.',
            'breathing_guide_fa': 'دم هنگام بالا بردن، بازدم هنگام پایین آوردن',
            'breathing_guide_en': 'Inhale when raising, exhale when pulling down',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["shoulder"]',
            'equipment_needed_fa': 'دستگاه لت',
            'equipment_needed_en': 'Lat Pulldown Machine'
        },
        
        # Functional - Home Category
        {
            'category': EXERCISE_CATEGORY_FUNCTIONAL_HOME,
            'name_fa': 'شنا',
            'name_en': 'Push-ups',
            'target_muscle_fa': 'سینه، شانه، سه‌سر بازو، شکم',
            'target_muscle_en': 'Chest, Shoulders, Triceps, Core',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': 'بدن را در یک خط مستقیم نگه دارید. به آرامی پایین بیایید و بالا بروید.',
            'execution_tips_en': 'Keep your body in a straight line. Lower and raise yourself slowly.',
            'breathing_guide_fa': 'دم هنگام پایین آمدن، بازدم هنگام بالا رفتن',
            'breathing_guide_en': 'Inhale when going down, exhale when pushing up',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["shoulder", "wrist"]',
            'equipment_needed_fa': 'بدون وسیله',
            'equipment_needed_en': 'No equipment'
        },
        {
            'category': EXERCISE_CATEGORY_FUNCTIONAL_HOME,
            'name_fa': 'اسکوات',
            'name_en': 'Squats',
            'target_muscle_fa': 'چهارسر ران، باسن، همسترینگ',
            'target_muscle_en': 'Quadriceps, Glutes, Hamstrings',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_LIGHT,
            'execution_tips_fa': 'پاها به عرض شانه. زانوها را به سمت انگشتان پا خم کنید. باسن را به عقب ببرید.',
            'execution_tips_en': 'Feet shoulder-width apart. Bend knees toward toes. Push hips back.',
            'breathing_guide_fa': 'دم هنگام پایین رفتن، بازدم هنگام بالا آمدن',
            'breathing_guide_en': 'Inhale when going down, exhale when coming up',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["knee", "lower_back"]',
            'equipment_needed_fa': 'بدون وسیله',
            'equipment_needed_en': 'No equipment'
        },
        {
            'category': EXERCISE_CATEGORY_FUNCTIONAL_HOME,
            'name_fa': 'پلانک',
            'name_en': 'Plank',
            'target_muscle_fa': 'شکم، شانه، کمر',
            'target_muscle_en': 'Core, Shoulders, Back',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': 'بدن را در یک خط مستقیم نگه دارید. سر، شانه، باسن و پاها در یک خط.',
            'execution_tips_en': 'Keep your body in a straight line. Head, shoulders, hips, and feet aligned.',
            'breathing_guide_fa': 'تنفس طبیعی و عمیق',
            'breathing_guide_en': 'Natural and deep breathing',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["shoulder", "lower_back"]',
            'equipment_needed_fa': 'بدون وسیله',
            'equipment_needed_en': 'No equipment'
        },
        {
            'category': EXERCISE_CATEGORY_FUNCTIONAL_HOME,
            'name_fa': 'برپی',
            'name_en': 'Burpee',
            'target_muscle_fa': 'تمام بدن',
            'target_muscle_en': 'Full Body',
            'level': TRAINING_LEVEL_INTERMEDIATE,
            'intensity': INTENSITY_HEAVY,
            'execution_tips_fa': 'شنا، سپس پرش به جلو، سپس اسکوات و پرش به بالا. حرکت را به صورت روان انجام دهید.',
            'execution_tips_en': 'Push-up, then jump forward, then squat and jump up. Perform the movement smoothly.',
            'breathing_guide_fa': 'تنفس ریتمیک و کنترل شده',
            'breathing_guide_en': 'Rhythmic and controlled breathing',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["knee", "shoulder", "lower_back"]',
            'equipment_needed_fa': 'بدون وسیله',
            'equipment_needed_en': 'No equipment'
        },
        
        # Hybrid / HIIT + Machine Category
        {
            'category': EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE,
            'name_fa': 'دویدن روی تردمیل با اینتروال',
            'name_en': 'Treadmill Interval Running',
            'target_muscle_fa': 'پاها، قلب و عروق',
            'target_muscle_en': 'Legs, Cardiovascular',
            'level': TRAINING_LEVEL_INTERMEDIATE,
            'intensity': INTENSITY_HEAVY,
            'execution_tips_fa': '۳۰ ثانیه دویدن سریع، ۳۰ ثانیه راه رفتن. این چرخه را ۱۰-۱۵ بار تکرار کنید.',
            'execution_tips_en': '30 seconds fast running, 30 seconds walking. Repeat this cycle 10-15 times.',
            'breathing_guide_fa': 'تنفس عمیق و منظم. از طریق بینی دم و از طریق دهان بازدم.',
            'breathing_guide_en': 'Deep and regular breathing. Inhale through nose, exhale through mouth.',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["knee", "ankle"]',
            'equipment_needed_fa': 'تردمیل',
            'equipment_needed_en': 'Treadmill'
        },
        {
            'category': EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE,
            'name_fa': 'دوچرخه ثابت با اینتروال',
            'name_en': 'Stationary Bike Intervals',
            'target_muscle_fa': 'پاها، قلب و عروق',
            'target_muscle_en': 'Legs, Cardiovascular',
            'level': TRAINING_LEVEL_BEGINNER,
            'intensity': INTENSITY_MEDIUM,
            'execution_tips_fa': '۲ دقیقه پدال زدن متوسط، ۳۰ ثانیه پدال زدن سریع. تکرار کنید.',
            'execution_tips_en': '2 minutes moderate pedaling, 30 seconds fast pedaling. Repeat.',
            'breathing_guide_fa': 'تنفس منظم و عمیق',
            'breathing_guide_en': 'Regular and deep breathing',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["knee"]',
            'equipment_needed_fa': 'دوچرخه ثابت',
            'equipment_needed_en': 'Stationary Bike'
        },
        {
            'category': EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE,
            'name_fa': 'روئینگ ماشین با اینتروال',
            'name_en': 'Rowing Machine Intervals',
            'target_muscle_fa': 'تمام بدن، قلب و عروق',
            'target_muscle_en': 'Full Body, Cardiovascular',
            'level': TRAINING_LEVEL_INTERMEDIATE,
            'intensity': INTENSITY_HEAVY,
            'execution_tips_fa': '۳۰ ثانیه پارو زدن سریع، ۳۰ ثانیه استراحت. کمر را صاف نگه دارید.',
            'execution_tips_en': '30 seconds fast rowing, 30 seconds rest. Keep your back straight.',
            'breathing_guide_fa': 'بازدم هنگام کشیدن، دم هنگام برگشت',
            'breathing_guide_en': 'Exhale when pulling, inhale when returning',
            'gender_suitability': GENDER_BOTH,
            'injury_contraindications': '["lower_back", "shoulder"]',
            'equipment_needed_fa': 'ماشین روئینگ',
            'equipment_needed_en': 'Rowing Machine'
        }
    ]
    
    for exercise_data in exercises:
        exercise = Exercise(**exercise_data)
        db.session.add(exercise)
    
    print(f'Added {len(exercises)} exercises to the library')
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        # Check if exercises already exist
        if Exercise.query.count() == 0:
            seed_exercises()
            print('Exercise library seeded successfully!')
        else:
            print(f'Exercise library already has {Exercise.query.count()} exercises. Skipping seed.')

