"""
Workout Plan Generator - 6-Month Personalized Plan
Generates progressive workout plans with Persian fitness terminology
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app import db
from models import UserProfile, Exercise, ExerciseHistory
import json
import random

# Persian Fitness Terminology
PERSIAN_TERMS = {
    'warm_up': 'گرم کردن',
    'cool_down': 'سرد کردن',
    'stretching': 'کشش',
    'sets': 'ست',
    'reps': 'تکرار',
    'rest': 'استراحت',
    'breathing_in': 'دم',
    'breathing_out': 'بازدم',
    'form': 'فرم',
    'control': 'کنترل',
    'explosive': 'انفجاری',
    'superset': 'سوپرست',
    'circuit': 'دایره',
    'interval': 'اینتروال',
    'rest_between_sets': 'استراحت بین ست‌ها',
    'rest_between_exercises': 'استراحت بین تمرینات',
    'focus': 'تمرکز',
    'intensity': 'شدت',
    'progression': 'پیشرفت',
    'stabilization': 'تثبیت',
    'challenge': 'چالش'
}

# Monthly Progression Rules
MONTHLY_RULES = {
    1: {
        'name_fa': 'آموزش فرم و تنفس',
        'name_en': 'Form and Breathing Training',
        'focus': ['form', 'control', 'breathing'],
        'sets_range': (2, 3),
        'reps_range': (8, 12),
        'rest_seconds': 60,
        'intensity': 'light',
        'include_advanced': False,
        'include_hybrid': False,
        'include_explosive': False,
        'include_supersets': False,
        'breathing_emphasis': True
    },
    2: {
        'name_fa': 'افزایش تکرار و ست',
        'name_en': 'Increase Reps and Sets',
        'focus': ['volume', 'endurance'],
        'sets_range': (3, 4),
        'reps_range': (12, 15),
        'rest_seconds': 60,
        'intensity': 'light',
        'include_advanced': False,
        'include_hybrid': False,
        'include_explosive': False,
        'include_supersets': False,
        'breathing_emphasis': True
    },
    3: {
        'name_fa': 'حرکات ترکیبی و پیشرفته',
        'name_en': 'Hybrid and Advanced Movements',
        'focus': ['hybrid', 'progression'],
        'sets_range': (3, 4),
        'reps_range': (10, 12),
        'rest_seconds': 90,
        'intensity': 'medium',
        'include_advanced': True,
        'include_hybrid': True,
        'include_explosive': False,
        'include_supersets': False,
        'breathing_emphasis': True
    },
    4: {
        'name_fa': 'حرکات انفجاری',
        'name_en': 'Explosive Movements',
        'focus': ['explosive', 'power'],
        'sets_range': (3, 4),
        'reps_range': (8, 10),
        'rest_seconds': 120,
        'intensity': 'heavy',
        'include_advanced': True,
        'include_hybrid': True,
        'include_explosive': True,
        'include_supersets': False,
        'breathing_emphasis': True
    },
    5: {
        'name_fa': 'افزایش شدت و سوپرست',
        'name_en': 'Increase Intensity and Supersets',
        'focus': ['intensity', 'supersets'],
        'sets_range': (4, 5),
        'reps_range': (8, 12),
        'rest_seconds': 60,
        'intensity': 'heavy',
        'include_advanced': True,
        'include_hybrid': True,
        'include_explosive': True,
        'include_supersets': True,
        'breathing_emphasis': True
    },
    6: {
        'name_fa': 'تثبیت و چالش',
        'name_en': 'Stabilization and Challenge',
        'focus': ['stabilization', 'challenge'],
        'sets_range': (4, 5),
        'reps_range': (10, 15),
        'rest_seconds': 90,
        'intensity': 'heavy',
        'include_advanced': True,
        'include_hybrid': True,
        'include_explosive': True,
        'include_supersets': True,
        'breathing_emphasis': True
    }
}

class WorkoutPlanGenerator:
    """Generates 6-month personalized workout plans"""
    
    def __init__(self, user_id: int, language: str = 'fa'):
        self.user_id = user_id
        self.language = language
        self.user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        self.workout_days_per_week = self.user_profile.workout_days_per_week if self.user_profile else 3
        
    def get_breathing_instruction(self, exercise: Exercise, month: int) -> str:
        """Generate breathing instruction in Persian"""
        if self.language == 'fa':
            if exercise.breathing_guide_fa:
                base_instruction = exercise.breathing_guide_fa
            else:
                base_instruction = f"{PERSIAN_TERMS['breathing_in']} هنگام پایین آوردن، {PERSIAN_TERMS['breathing_out']} هنگام بالا بردن"
            
            if month == 1:
                return f"{base_instruction}. {PERSIAN_TERMS['focus']} بر {PERSIAN_TERMS['breathing_in']} و {PERSIAN_TERMS['breathing_out']} عمیق و کنترل شده."
            elif month <= 3:
                return f"{base_instruction}. تنفس ریتمیک و هماهنگ با حرکت."
            else:
                return f"{base_instruction}. تنفس قدرتمند و کنترل شده."
        else:
            if exercise.breathing_guide_en:
                return exercise.breathing_guide_en
            return "Inhale when lowering, exhale when pushing up"
    
    def get_exercise_selection_criteria(self, month: int) -> Dict[str, Any]:
        """Get criteria for exercise selection based on month and user profile"""
        rules = MONTHLY_RULES[month]
        
        # Get user injuries and medical conditions
        user_injuries = []
        medical_conditions = []
        if self.user_profile:
            user_injuries = self.user_profile.get_injuries()
            medical_conditions = self.user_profile.get_medical_conditions()
        
        # Combine for safety filtering
        safety_concerns = list(set(user_injuries + medical_conditions))
        
        criteria = {
            'level': self.user_profile.training_level if self.user_profile else 'beginner',
            'intensity': rules['intensity'],
            'include_advanced': rules['include_advanced'],
            'include_hybrid': rules['include_hybrid'],
            'include_explosive': rules['include_explosive'],
            'equipment_filter': self._get_equipment_filter(),
            'injuries': safety_concerns,
            'fitness_goals': self.user_profile.get_fitness_goals() if self.user_profile else [],
            'age': self.user_profile.age if self.user_profile else None,
            'gender': self.user_profile.gender if self.user_profile else None
        }
        
        return criteria
    
    def _get_equipment_filter(self) -> str:
        """Determine equipment filter based on user profile"""
        if not self.user_profile:
            return 'home'
        
        if self.user_profile.gym_access:
            return 'all'
        
        return 'home'
    
    def select_exercises_for_week(
        self, 
        month: int, 
        week: int, 
        muscle_groups: List[str],
        exercise_pool: List[Exercise]
    ) -> List[Exercise]:
        """Select exercises for a specific week"""
        rules = MONTHLY_RULES[month]
        selected = []
        
        # Filter exercise pool based on month rules
        filtered_pool = []
        for ex in exercise_pool:
            # Check level
            if ex.level != rules.get('level', ex.level):
                if month == 1 and ex.level != 'beginner':
                    continue
                if month == 2 and ex.level not in ['beginner', 'intermediate']:
                    continue
            
            # Check intensity
            if ex.intensity != rules['intensity']:
                # Allow progression
                intensity_order = ['light', 'medium', 'heavy']
                current_idx = intensity_order.index(rules['intensity'])
                ex_idx = intensity_order.index(ex.intensity)
                if ex_idx > current_idx + 1:
                    continue
            
            # Check advanced/hybrid/explosive
            if not rules['include_advanced'] and ex.level == 'advanced':
                continue
            
            if not rules['include_hybrid'] and ex.category == 'hybrid_hiit_machine':
                continue
            
            # Note: Explosive is determined by exercise name/metadata, not category
            # This would need to be added to exercise metadata
            
            filtered_pool.append(ex)
        
        # Select exercises for each muscle group
        for muscle_group in muscle_groups:
            # Find exercises targeting this muscle
            muscle_exercises = [
                ex for ex in filtered_pool
                if muscle_group.lower() in ex.target_muscle_en.lower() or
                   muscle_group.lower() in ex.target_muscle_fa.lower()
            ]
            
            if muscle_exercises:
                selected.append(random.choice(muscle_exercises))
        
        return selected
    
    def generate_weekly_workout(
        self, 
        month: int, 
        week: int, 
        day: int,
        exercises: List[Exercise]
    ) -> Dict[str, Any]:
        """Generate workout for a specific day"""
        rules = MONTHLY_RULES[month]
        
        # Determine sets and reps
        sets = random.randint(*rules['sets_range'])
        reps = random.randint(*rules['reps_range'])
        
        # Adjust for month progression
        if month == 1:
            reps = random.randint(8, 12)
        elif month == 2:
            reps = random.randint(12, 15)
        elif month >= 4:
            if rules['include_explosive']:
                reps = random.randint(6, 10)
        
        workout_exercises = []
        
        for exercise in exercises:
            breathing_note = self.get_breathing_instruction(exercise, month)
            
            exercise_data = {
                'exercise_id': exercise.id,
                'name_fa': exercise.name_fa,
                'name_en': exercise.name_en,
                'target_muscle_fa': exercise.target_muscle_fa,
                'target_muscle_en': exercise.target_muscle_en,
                'sets': sets,
                'reps': reps,
                'rest_seconds': rules['rest_seconds'],
                'breathing_note_fa': breathing_note,
                'breathing_note_en': exercise.breathing_guide_en or "Inhale when lowering, exhale when pushing up",
                'form_tips_fa': exercise.execution_tips_fa or f"{PERSIAN_TERMS['focus']} بر {PERSIAN_TERMS['form']} صحیح",
                'form_tips_en': exercise.execution_tips_en or "Focus on proper form",
                'intensity': exercise.intensity,
                'category': exercise.category
            }
            
            workout_exercises.append(exercise_data)
        
        # Add supersets if applicable
        if rules['include_supersets'] and len(workout_exercises) >= 2:
            # Group exercises into supersets
            superset_groups = []
            for i in range(0, len(workout_exercises), 2):
                if i + 1 < len(workout_exercises):
                    superset_groups.append([
                        workout_exercises[i],
                        workout_exercises[i + 1]
                    ])
                else:
                    superset_groups.append([workout_exercises[i]])
            
            return {
                'day': day,
                'month': month,
                'week': week,
                'workout_type_fa': 'سوپرست' if rules['include_supersets'] else 'تمرین معمولی',
                'workout_type_en': 'Superset' if rules['include_supersets'] else 'Regular Workout',
                'exercises': workout_exercises,
                'supersets': superset_groups if rules['include_supersets'] else None,
                'total_duration_minutes': len(workout_exercises) * (sets * (reps * 2) + rules['rest_seconds']) // 60,
                'focus_fa': rules['name_fa'],
                'focus_en': rules['name_en']
            }
        
        return {
            'day': day,
            'month': month,
            'week': week,
            'workout_type_fa': 'تمرین معمولی',
            'workout_type_en': 'Regular Workout',
            'exercises': workout_exercises,
            'total_duration_minutes': len(workout_exercises) * (sets * (reps * 2) + rules['rest_seconds']) // 60,
            'focus_fa': rules['name_fa'],
            'focus_en': rules['name_en']
        }
    
    def generate_6_month_plan(self, exercise_pool: List[Exercise]) -> Dict[str, Any]:
        """Generate complete 6-month workout plan"""
        
        # Define muscle groups for split
        muscle_groups = {
            'push': ['chest', 'shoulders', 'triceps', 'سینه', 'شانه', 'سه‌سر'],
            'pull': ['back', 'biceps', 'lats', 'پشت', 'دو سر', 'لات'],
            'legs': ['legs', 'quads', 'hamstrings', 'glutes', 'پا', 'چهارسر', 'همسترینگ', 'باسن'],
            'core': ['core', 'abs', 'شکم', 'میانه'],
            'full_body': ['full body', 'تمام بدن']
        }
        
        plan = {
            'user_id': self.user_id,
            'generated_at': datetime.utcnow().isoformat(),
            'language': self.language,
            'total_duration_months': 6,
            'workout_days_per_week': self.workout_days_per_week,
            'months': {}
        }
        
        # Generate plan for each month
        for month in range(1, 7):
            month_data = {
                'month_number': month,
                'month_name_fa': MONTHLY_RULES[month]['name_fa'],
                'month_name_en': MONTHLY_RULES[month]['name_en'],
                'focus_fa': MONTHLY_RULES[month]['name_fa'],
                'focus_en': MONTHLY_RULES[month]['name_en'],
                'weeks': {}
            }
            
            # Generate 4 weeks per month
            for week in range(1, 5):
                week_data = {
                    'week_number': week,
                    'days': {}
                }
                
                # Generate workouts for each workout day
                for day in range(1, self.workout_days_per_week + 1):
                    # Rotate muscle groups
                    if day == 1:
                        target_groups = muscle_groups['push']
                    elif day == 2:
                        target_groups = muscle_groups['pull']
                    elif day == 3:
                        target_groups = muscle_groups['legs']
                    elif day == 4:
                        target_groups = muscle_groups['core']
                    else:
                        target_groups = muscle_groups['full_body']
                    
                    # Select exercises
                    selected_exercises = self.select_exercises_for_week(
                        month, week, target_groups, exercise_pool
                    )
                    
                    if selected_exercises:
                        workout = self.generate_weekly_workout(
                            month, week, day, selected_exercises
                        )
                        week_data['days'][f'day_{day}'] = workout
                
                month_data['weeks'][f'week_{week}'] = week_data
            
            plan['months'][f'month_{month}'] = month_data
        
        return plan
    
    def format_plan_for_table(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Format plan as weekly table structure"""
        table_format = {
            'plan_summary': {
                'total_months': 6,
                'workout_days_per_week': plan['workout_days_per_week'],
                'generated_at': plan['generated_at']
            },
            'weekly_tables': {}
        }
        
        for month_key, month_data in plan['months'].items():
            month_num = month_data['month_number']
            
            for week_key, week_data in month_data['weeks'].items():
                week_num = week_data['week_number']
                
                table_key = f"month_{month_num}_week_{week_num}"
                
                weekly_table = {
                    'month': month_num,
                    'week': week_num,
                    'month_focus_fa': month_data['focus_fa'],
                    'month_focus_en': month_data['focus_en'],
                    'workouts': []
                }
                
                for day_key, day_workout in week_data['days'].items():
                    workout_row = {
                        'day': day_workout['day'],
                        'workout_type_fa': day_workout['workout_type_fa'],
                        'workout_type_en': day_workout['workout_type_en'],
                        'exercises': []
                    }
                    
                    for exercise in day_workout['exercises']:
                        exercise_row = {
                            'exercise_name_fa': exercise['name_fa'],
                            'exercise_name_en': exercise['name_en'],
                            'target_muscle_fa': exercise['target_muscle_fa'],
                            'sets': exercise['sets'],
                            'reps': exercise['reps'],
                            'rest_seconds': exercise['rest_seconds'],
                            'breathing_note_fa': exercise['breathing_note_fa'],
                            'form_tips_fa': exercise['form_tips_fa']
                        }
                        workout_row['exercises'].append(exercise_row)
                    
                    if day_workout.get('supersets'):
                        workout_row['supersets'] = []
                        for superset_pair in day_workout['supersets']:
                            superset_data = []
                            for ex in superset_pair:
                                superset_data.append({
                                    'exercise_name_fa': ex['name_fa'],
                                    'sets': ex['sets'],
                                    'reps': ex['reps'],
                                    'breathing_note_fa': ex['breathing_note_fa']
                                })
                            workout_row['supersets'].append(superset_data)
                    
                    weekly_table['workouts'].append(workout_row)
                
                table_format['weekly_tables'][table_key] = weekly_table
        
        return table_format

