"""
Persian Fitness Coach AI Agent
Professional, empathetic coach that provides safe, personalized workout plans
"""

from typing import Dict, List, Any, Optional
from app import db
from models import Exercise, UserProfile
from models_workout_log import WorkoutLog, ProgressEntry
from services.workout_plan_generator import WorkoutPlanGenerator, MONTHLY_RULES
from services.adaptive_feedback import AdaptiveFeedbackService
import json
import re

# Persian Professional Fitness Terminology
PERSIAN_TERMS = {
    'warm_up': 'گرم کردن',
    'cool_down': 'سرد کردن',
    'sets': 'ست',
    'reps': 'تکرار',
    'rest': 'استراحت',
    'breathing_in': 'دم',
    'breathing_out': 'بازدم',
    'form': 'فرم',
    'technique': 'تکنیک',
    'intensity': 'شدت',
    'progression': 'پیشرفت',
    'periodization': 'دوره‌بندی',
    'muscle_group': 'گروه عضلانی',
    'target_muscle': 'عضله هدف',
    'contraindication': 'ممنوعیت',
    'alternative': 'جایگزین',
    'workout': 'تمرین',
    'exercise': 'حرکت',
    'training': 'تمرینات',
    'fitness': 'تناسب اندام',
    'strength': 'قدرت',
    'endurance': 'استقامت',
    'flexibility': 'انعطاف‌پذیری',
    'cardio': 'کاردیو',
    'resistance': 'مقاومتی'
}

class PersianFitnessCoachAI:
    """Persian-speaking Fitness Coach AI Agent"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        self.user = User.query.get(user_id)
        
    def detect_injuries_in_message(self, message: str) -> List[str]:
        """Detect mentioned injuries in Persian message"""
        injury_keywords = {
            'کمردرد': 'lower_back',
            'درد کمر': 'lower_back',
            'زانو درد': 'knee',
            'درد زانو': 'knee',
            'شانه درد': 'shoulder',
            'درد شانه': 'shoulder',
            'گردن درد': 'neck',
            'درد گردن': 'neck',
            'مچ دست': 'wrist',
            'مچ پا': 'ankle',
            'آرنج': 'elbow',
            'درد آرنج': 'elbow',
            'مچ پا': 'ankle',
            'درد مچ پا': 'ankle'
        }
        
        detected = []
        message_lower = message.lower()
        
        for persian_term, injury_type in injury_keywords.items():
            if persian_term in message_lower:
                detected.append(injury_type)
        
        return detected
    
    def get_safe_exercises(self, exercise_pool: List[Exercise], user_injuries: List[str]) -> List[Exercise]:
        """Filter exercises to exclude those with injury contraindications"""
        safe_exercises = []
        
        for exercise in exercise_pool:
            contraindications = []
            if hasattr(exercise, 'get_injury_contraindications'):
                contraindications = exercise.get_injury_contraindications()
            elif exercise.injury_contraindications:
                try:
                    contraindications = json.loads(exercise.injury_contraindications)
                except:
                    contraindications = []
            
            # Check if any user injury matches contraindications
            is_safe = True
            for injury in user_injuries:
                injury_lower = injury.lower()
                for contra in contraindications:
                    if injury_lower in contra.lower() or contra.lower() in injury_lower:
                        is_safe = False
                        break
                if not is_safe:
                    break
            
            if is_safe:
                safe_exercises.append(exercise)
        
        return safe_exercises
    
    def format_workout_table_markdown(
        self,
        exercises: List[Exercise],
        month: int,
        day_name: str = "روز تمرین"
    ) -> str:
        """Format workout plan as Markdown table with Persian terminology"""
        rules = MONTHLY_RULES[month]
        sets = rules['sets_range'][1]  # Use max sets
        reps = rules['reps_range'][1]  # Use max reps
        
        table = f"\n## {day_name}\n\n"
        table += "| حرکت | عضله هدف | ست | تکرار | استراحت | تنفس و نکات |\n"
        table += "|------|----------|-----|--------|----------|-------------|\n"
        
        for exercise in exercises:
            # Get breathing instruction
            breathing = exercise.breathing_guide_fa or "دم هنگام پایین آوردن، بازدم هنگام بالا بردن"
            
            # Add month-specific breathing emphasis
            if month == 1:
                breathing += ". تمرکز بر تنفس عمیق و کنترل شده"
            elif month <= 3:
                breathing += ". تنفس ریتمیک و هماهنگ"
            else:
                breathing += ". تنفس قدرتمند و کنترل شده"
            
            # Get form tips
            form_tips = exercise.execution_tips_fa or "فرم صحیح را حفظ کنید"
            
            # Combine breathing and tips
            breathing_tips = f"{breathing}. {form_tips}"
            
            table += f"| {exercise.name_fa} | {exercise.target_muscle_fa} | {sets} | {reps} | {rules['rest_seconds']}s | {breathing_tips} |\n"
        
        return table
    
    def generate_personalized_response(
        self,
        user_message: str,
        exercise_pool: List[Exercise] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized Persian response based on user message
        Uses Vector DB to retrieve exercises, checks safety, follows periodization
        """
        
        # Detect injuries in message
        detected_injuries = self.detect_injuries_in_message(user_message)
        
        # Get user's existing injuries and medical conditions
        user_injuries = []
        medical_conditions = []
        if self.user_profile:
            user_injuries = self.user_profile.get_injuries()
            medical_conditions = self.user_profile.get_medical_conditions()
        
        # Combine detected and existing injuries
        all_injuries = list(set(user_injuries + detected_injuries))
        
        # Add medical conditions to safety considerations
        # Medical conditions may require special exercise modifications
        if medical_conditions:
            all_injuries.extend([c for c in medical_conditions if c not in all_injuries])
        
        # Determine user's current month in program (if applicable)
        # For now, default to month 1 for new users
        current_month = 1
        
        # Check if user has workout history to determine progression
        recent_logs = WorkoutLog.query.filter_by(user_id=self.user_id)\
            .order_by(WorkoutLog.workout_date.desc()).limit(10).all()
        
        if recent_logs:
            # Estimate month based on workout frequency and progression
            # This is simplified - in production, track actual month
            total_workouts = len(recent_logs)
            if total_workouts > 60:
                current_month = 6
            elif total_workouts > 50:
                current_month = 5
            elif total_workouts > 40:
                current_month = 4
            elif total_workouts > 30:
                current_month = 3
            elif total_workouts > 15:
                current_month = 2
        
        # Determine intent
        message_lower = user_message.lower()
        
        # Greeting
        if any(word in message_lower for word in ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'hello', 'hi']):
            return self._handle_greeting(all_injuries)
        
        # Request workout plan
        if any(word in message_lower for word in ['برنامه', 'تمرین', 'workout', 'plan', 'برنامه تمرین']):
            return self._handle_workout_plan_request(
                user_message, current_month, all_injuries, exercise_pool
            )
        
        # Report injury
        if detected_injuries or any(word in message_lower for word in ['درد', 'آسیب', 'pain', 'injury']):
            return self._handle_injury_report(detected_injuries, all_injuries)
        
        # Ask about exercise
        if any(word in message_lower for word in ['تمرین', 'حرکت', 'exercise', 'movement']):
            return self._handle_exercise_question(user_message, all_injuries, exercise_pool)
        
        # Progress check
        if any(word in message_lower for word in ['پیشرفت', 'progress', 'نتیجه', 'result']):
            return self._handle_progress_check()
        
        # General help
        return self._handle_general_help()
    
    def _handle_greeting(self, injuries: List[str]) -> Dict[str, Any]:
        """Handle greeting message"""
        greeting = "سلام! 👋\n\n"
        greeting += "من مربی شخصی شما هستم و آماده‌ام تا یک برنامه تمرینی کاملاً شخصی‌سازی شده برای شما طراحی کنم.\n\n"
        
        if injuries:
            greeting += f"⚠️ **توجه:** من متوجه شدم که شما {', '.join(injuries)} دارید. "
            greeting += "تمام تمرینات پیشنهادی با در نظر گیری این موضوع طراحی می‌شوند تا کاملاً ایمن باشند.\n\n"
        
        greeting += "چگونه می‌توانم به شما کمک کنم؟\n"
        greeting += "- می‌خواهید یک برنامه تمرینی دریافت کنید؟\n"
        greeting += "- سوالی در مورد تمرینات دارید؟\n"
        greeting += "- می‌خواهید پیشرفت خود را بررسی کنید؟"
        
        return {
            'response': greeting,
            'injuries_detected': injuries,
            'safety_checked': True
        }
    
    def _handle_workout_plan_request(
        self,
        message: str,
        month: int,
        injuries: List[str],
        exercise_pool: List[Exercise]
    ) -> Dict[str, Any]:
        """Handle workout plan request"""
        
        # Determine target muscle groups from message
        muscle_groups = self._extract_muscle_groups(message)
        
        # Get safe exercises
        if exercise_pool:
            safe_exercises = self.get_safe_exercises(exercise_pool, injuries)
        else:
            # Query exercises from database
            query = Exercise.query
            if self.user_profile and not self.user_profile.gym_access:
                query = query.filter(Exercise.category == 'functional_home')
            safe_exercises = self.get_safe_exercises(query.all(), injuries)
        
        # Filter by month rules
        rules = MONTHLY_RULES[month]
        filtered_exercises = []
        
        for exercise in safe_exercises:
            # Check level
            if month == 1 and exercise.level != 'beginner':
                continue
            if month == 2 and exercise.level == 'advanced':
                continue
            
            # Check intensity
            intensity_order = ['light', 'medium', 'heavy']
            current_idx = intensity_order.index(rules['intensity'])
            ex_idx = intensity_order.index(exercise.intensity)
            if ex_idx > current_idx:
                continue
            
            # Check category restrictions
            if not rules['include_hybrid'] and exercise.category == 'hybrid_hiit_machine':
                continue
            if not rules['include_advanced'] and exercise.level == 'advanced':
                continue
            
            filtered_exercises.append(exercise)
        
        # Select exercises for muscle groups
        selected_exercises = []
        if muscle_groups:
            for muscle in muscle_groups:
                matching = [
                    ex for ex in filtered_exercises
                    if muscle.lower() in ex.target_muscle_fa.lower() or
                       muscle.lower() in ex.target_muscle_en.lower()
                ]
                if matching:
                    selected_exercises.append(matching[0])
        else:
            # Select diverse exercises
            selected_exercises = filtered_exercises[:6]  # Limit to 6 exercises
        
        if not selected_exercises:
            return {
                'response': "متأسفانه با توجه به محدودیت‌های شما (آسیب‌ها یا تجهیزات)، "
                          "نمی‌توانم تمرین مناسبی پیدا کنم. لطفاً با پزشک یا فیزیوتراپیست مشورت کنید.",
                'exercises': [],
                'safety_checked': True
            }
        
        # Generate response
        response = f"## برنامه تمرینی - ماه {month}: {rules['name_fa']}\n\n"
        response += f"**تمرکز این ماه:** {rules['name_fa']}\n\n"
        
        if injuries:
            response += f"✅ **بررسی ایمنی:** تمام تمرینات با در نظر گیری {', '.join(injuries)} شما انتخاب شده‌اند.\n\n"
        
        # Add workout table
        response += self.format_workout_table_markdown(selected_exercises, month)
        
        response += f"\n\n### نکات مهم:\n"
        response += f"- **گرم کردن:** قبل از شروع، ۵-۱۰ دقیقه {PERSIAN_TERMS['warm_up']} انجام دهید\n"
        response += f"- **سرد کردن:** بعد از تمرین، ۵ دقیقه {PERSIAN_TERMS['cool_down']} و کشش\n"
        response += f"- **فرم صحیح:** در ماه اول، {PERSIAN_TERMS['focus']} اصلی بر {PERSIAN_TERMS['form']} و {PERSIAN_TERMS['technique']} است\n"
        response += f"- **پیشرفت تدریجی:** به آرامی {PERSIAN_TERMS['intensity']} را افزایش دهید\n\n"
        
        response += "💪 **موفق باشید!** اگر سوالی دارید یا نیاز به جایگزین دارید، بگویید."
        
        return {
            'response': response,
            'exercises': [ex.id for ex in selected_exercises],
            'month': month,
            'safety_checked': True,
            'injuries_considered': injuries
        }
    
    def _handle_injury_report(
        self,
        detected: List[str],
        all_injuries: List[str]
    ) -> Dict[str, Any]:
        """Handle injury report"""
        response = "⚠️ **توجه به ایمنی شما:**\n\n"
        
        if detected:
            response += f"متوجه شدم که شما {', '.join(detected)} دارید. "
        
        response += "تمام تمرینات پیشنهادی من با بررسی دقیق ممنوعیت‌های آسیب (Injury Contraindications) "
        response += "انتخاب می‌شوند تا کاملاً ایمن باشند.\n\n"
        
        response += "**توصیه‌های ایمنی:**\n"
        response += "1. قبل از شروع هر برنامه تمرینی، با پزشک یا فیزیوتراپیست مشورت کنید\n"
        response += "2. اگر در حین تمرین درد احساس کردید، فوراً متوقف کنید\n"
        response += "3. من همیشه تمرینات جایگزین ایمن برای شما پیشنهاد می‌دهم\n\n"
        
        response += "آیا می‌خواهید یک برنامه تمرینی ایمن برای شما طراحی کنم؟"
        
        return {
            'response': response,
            'injuries_detected': detected,
            'safety_checked': True
        }
    
    def _handle_exercise_question(
        self,
        message: str,
        injuries: List[str],
        exercise_pool: List[Exercise]
    ) -> Dict[str, Any]:
        """Handle exercise-specific questions"""
        # Extract exercise name or muscle group
        muscle_groups = self._extract_muscle_groups(message)
        
        if not exercise_pool:
            exercise_pool = Exercise.query.all()
        
        safe_exercises = self.get_safe_exercises(exercise_pool, injuries)
        
        if muscle_groups:
            matching = [
                ex for ex in safe_exercises
                if any(mg.lower() in ex.target_muscle_fa.lower() for mg in muscle_groups)
            ]
            
            if matching:
                exercise = matching[0]
                response = f"## {exercise.name_fa}\n\n"
                response += f"**عضله هدف:** {exercise.target_muscle_fa}\n"
                response += f"**سطح:** {exercise.level}\n"
                response += f"**شدت:** {exercise.intensity}\n\n"
                response += f"### نکات اجرا:\n{exercise.execution_tips_fa or 'فرم صحیح را حفظ کنید'}\n\n"
                response += f"### تنفس:\n{exercise.breathing_guide_fa or 'دم هنگام پایین آوردن، بازدم هنگام بالا بردن'}\n"
                
                if injuries:
                    response += f"\n✅ این تمرین برای {', '.join(injuries)} شما ایمن است."
                
                return {
                    'response': response,
                    'exercise_id': exercise.id,
                    'safety_checked': True
                }
        
        return {
            'response': "لطفاً نام عضله یا تمرین مورد نظر را مشخص کنید تا اطلاعات دقیق‌تری ارائه دهم.",
            'safety_checked': True
        }
    
    def _handle_progress_check(self) -> Dict[str, Any]:
        """Handle progress check request"""
        # Get recent progress entries
        recent_progress = ProgressEntry.query.filter_by(user_id=self.user_id)\
            .order_by(ProgressEntry.recorded_at.desc()).limit(2).all()
        
        if not recent_progress:
            return {
                'response': "هنوز اطلاعات پیشرفتی ثبت نشده است. "
                          "لطفاً وزن و اندازه‌گیری‌های خود را ثبت کنید تا بتوانم پیشرفت شما را بررسی کنم.",
                'has_progress': False
            }
        
        response = "## بررسی پیشرفت شما 📊\n\n"
        
        if len(recent_progress) >= 2:
            old = recent_progress[1]
            new = recent_progress[0]
            
            if old.weight_kg and new.weight_kg:
                diff = new.weight_kg - old.weight_kg
                if diff > 0:
                    response += f"📈 **وزن:** {old.weight_kg} → {new.weight_kg} کیلوگرم (+{diff:.1f} کیلوگرم)\n"
                elif diff < 0:
                    response += f"📉 **وزن:** {old.weight_kg} → {new.weight_kg} کیلوگرم ({diff:.1f} کیلوگرم)\n"
                else:
                    response += f"➡️ **وزن:** {new.weight_kg} کیلوگرم (بدون تغییر)\n"
        
        response += "\n💪 **ادامه دهید!** پیشرفت شما عالی است."
        
        return {
            'response': response,
            'has_progress': True
        }
    
    def _handle_general_help(self) -> Dict[str, Any]:
        """Handle general help request"""
        response = "## چگونه می‌توانم کمک کنم؟\n\n"
        response += "من می‌توانم در موارد زیر به شما کمک کنم:\n\n"
        response += "1. **طراحی برنامه تمرینی:** یک برنامه ۶ ماهه شخصی‌سازی شده\n"
        response += "2. **پیشنهاد تمرینات:** بر اساس اهداف و تجهیزات شما\n"
        response += "3. **بررسی ایمنی:** اطمینان از ایمن بودن تمرینات با توجه به آسیب‌ها\n"
        response += "4. **پیشنهاد جایگزین:** اگر تمرینی برای شما سخت است یا درد ایجاد می‌کند\n"
        response += "5. **پیگیری پیشرفت:** بررسی وزن، اندازه‌گیری‌ها و فرم\n\n"
        response += "لطفاً بگویید چه کمکی نیاز دارید؟"
        
        return {
            'response': response,
            'safety_checked': True
        }
    
    def _extract_muscle_groups(self, message: str) -> List[str]:
        """Extract muscle groups from Persian message"""
        muscle_keywords = {
            'سینه': 'chest',
            'پشت': 'back',
            'شانه': 'shoulder',
            'بازو': 'arm',
            'پا': 'leg',
            'باسن': 'glute',
            'شکم': 'abs',
            'کاردیو': 'cardio'
        }
        
        found = []
        message_lower = message.lower()
        
        for persian_term, english_term in muscle_keywords.items():
            if persian_term in message_lower:
                found.append(persian_term)
        
        return found

