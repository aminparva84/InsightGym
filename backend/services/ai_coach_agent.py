"""
Persian Fitness Coach AI Agent
Professional, empathetic coach that provides safe, personalized workout plans
"""

from typing import Dict, List, Any, Optional
from flask import current_app
from app import User
from models import Exercise, UserProfile


def _db():
    """Get SQLAlchemy instance from current Flask app context."""
    return current_app.extensions['sqlalchemy']
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
        db = _db()
        self.user_profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
        self.user = db.session.get(User, user_id)
        
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
    
    def _normalize_injury(self, injury: str) -> str:
        """Map Persian/common injury names to canonical English for matching."""
        if not injury or not isinstance(injury, str):
            return ''
        m = {
            'زانو': 'knee', 'کمردرد': 'lower_back', 'کمر': 'lower_back',
            'شانه': 'shoulder', 'گردن': 'neck', 'مچ دست': 'wrist', 'مچ پا': 'ankle',
            'آرنج': 'elbow', 'hip': 'hip', 'ران': 'hip',
        }
        s = injury.strip().lower()
        return m.get(s, s)

    def get_safe_exercises(self, exercise_pool: List[Exercise], user_injuries: List[str]) -> List[Exercise]:
        """Filter exercises to exclude those with injury contraindications.
        Also excludes exercises in admin's forbidden_movements for user's injuries."""
        safe_exercises = []
        normalized_injuries = [self._normalize_injury(i) for i in (user_injuries or []) if i]
        forbidden_names = self._get_forbidden_exercise_names(normalized_injuries)

        for exercise in exercise_pool:
            contraindications = []
            if hasattr(exercise, 'get_injury_contraindications'):
                contraindications = exercise.get_injury_contraindications()
            elif exercise.injury_contraindications:
                try:
                    contraindications = json.loads(exercise.injury_contraindications)
                except Exception:
                    contraindications = []

            # Check if any user injury matches contraindications
            is_safe = True
            for injury in normalized_injuries:
                injury_lower = injury.lower()
                for contra in contraindications:
                    c = (contra or '').lower()
                    if injury_lower in c or c in injury_lower:
                        is_safe = False
                        break
                if not is_safe:
                    break

            # Exclude if exercise name is in admin's forbidden_movements for user's injuries
            if is_safe and forbidden_names:
                ex_name_fa = (exercise.name_fa or '').strip().lower()
                ex_name_en = (exercise.name_en or '').strip().lower()
                for fn in forbidden_names:
                    fn_lower = fn.lower()
                    if fn_lower in ex_name_fa or fn_lower in ex_name_en or ex_name_fa in fn_lower or ex_name_en in fn_lower:
                        is_safe = False
                        break

            if is_safe:
                safe_exercises.append(exercise)

        return safe_exercises

    def _get_forbidden_exercise_names(self, injuries: List[str]) -> List[str]:
        """Load admin's forbidden_movements from Configuration.injuries for user's injury types."""
        if not injuries:
            return []
        try:
            from models import Configuration
            db = _db()
            config = db.session.query(Configuration).first()
            if not config or not config.injuries:
                return []
            raw = json.loads(config.injuries) if isinstance(config.injuries, str) else config.injuries
            names = []
            for inj in injuries:
                inj_key = inj.replace(' ', '_').lower()
                entry = raw.get(inj_key) or raw.get(inj) or {}
                forbidden = entry.get('forbidden_movements') or []
                for m in forbidden:
                    if isinstance(m, dict):
                        names.extend([m.get('fa', ''), m.get('en', '')])
                    elif isinstance(m, str) and m.strip():
                        names.append(m.strip())
            return [n for n in names if n]
        except Exception:
            return []

    def _get_injury_important_notes(self, injuries: List[str], language: str = "fa") -> str:
        """Get admin's important_notes for user's injuries from Configuration.injuries."""
        if not injuries:
            return ""
        try:
            from models import Configuration
            db = _db()
            config = db.session.query(Configuration).first()
            if not config or not config.injuries:
                return ""
            raw = json.loads(config.injuries) if isinstance(config.injuries, str) else config.injuries
            parts = []
            field = 'important_notes_fa' if language == 'fa' else 'important_notes_en'
            seen_notes = set()
            for inj in injuries:
                norm = self._normalize_injury(inj)
                inj_key = (norm or inj).replace(' ', '_').lower()
                entry = raw.get(inj_key) or raw.get(inj) or {}
                note = (entry.get(field) or '').strip()
                if note and note not in seen_notes:
                    seen_notes.add(note)
                    parts.append(f"- {note}")
            common = (raw.get('common_injury_note_fa' if language == 'fa' else 'common_injury_note_en') or '').strip()
            if common:
                parts.insert(0, common)
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    def _get_training_levels_config(self, language: str = "fa") -> Optional[Dict]:
        """Load admin's Training Levels Info (Training Info tab) for user's level and goal."""
        try:
            from models import Configuration
            db = _db()
            config = db.session.query(Configuration).first()
            if not config or not config.training_levels:
                return None
            raw = json.loads(config.training_levels) if isinstance(config.training_levels, str) else config.training_levels
            if not raw:
                return None
            level = (self.user_profile.training_level or 'beginner').strip().lower()
            goals = self.user_profile.get_fitness_goals() if self.user_profile and hasattr(self.user_profile, 'get_fitness_goals') else []
            purpose = 'gain_muscle'
            goal_to_purpose = {
                'lose_weight': 'lose_weight', 'کاهش وزن': 'lose_weight', 'weight_loss': 'lose_weight',
                'gain_weight': 'gain_weight', 'افزایش وزن': 'gain_weight',
                'gain_muscle': 'gain_muscle', 'افزایش عضله': 'gain_muscle',
                'muscle_gain': 'gain_muscle', 'strength': 'gain_muscle',
                'shape_fitting': 'shape_fitting', 'تناسب اندام': 'shape_fitting',
                'endurance': 'shape_fitting',
            }
            for g in (goals or []):
                g_lower = (g or '').strip().lower()
                if g_lower in goal_to_purpose:
                    purpose = goal_to_purpose[g_lower]
                    break
            level_data = raw.get(level) or raw.get('beginner') or {}
            purposes = level_data.get('purposes') or {}
            purpose_data = purposes.get(purpose) or purposes.get('gain_muscle') or {}
            training_focus = (purpose_data.get('training_focus_fa') if language == 'fa' else purpose_data.get('training_focus_en')) or ''
            return {
                'level': level,
                'purpose': purpose,
                'training_levels': raw,
                'training_focus': training_focus.strip() if training_focus else None,
            }
        except Exception:
            return None

    def format_workout_table_markdown(
        self,
        exercises: List[Exercise],
        month: int,
        day_name: str = "روز تمرین",
        language: str = "fa",
        training_levels_config: Optional[Dict] = None
    ) -> str:
        """Format workout plan as Markdown table. Uses admin's Training Levels Info (sets, reps, focus) when provided."""
        rules = MONTHLY_RULES[month]
        sets = rules['sets_range'][1]  # Use max sets
        reps = rules['reps_range'][1]  # Use max reps
        rest_seconds = rules.get('rest_seconds', 60)

        # Override with admin's Training Levels Info if provided
        if training_levels_config:
            level_key = (training_levels_config.get('level') or 'beginner').strip().lower()
            purpose_key = (training_levels_config.get('purpose') or 'gain_muscle').strip().lower()
            level_data = training_levels_config.get('training_levels', {}).get(level_key, {})
            purposes = level_data.get('purposes') or {}
            purpose_data = purposes.get(purpose_key) or purposes.get('gain_muscle') or {}
            if purpose_data.get('sets_per_action'):
                try:
                    sets = int(purpose_data['sets_per_action'])
                except (ValueError, TypeError):
                    pass
            if purpose_data.get('reps_per_action'):
                try:
                    reps = int(purpose_data['reps_per_action'])
                except (ValueError, TypeError):
                    pass
            if purpose_data.get('break_between_sets'):
                try:
                    rest_seconds = int(purpose_data['break_between_sets'])
                except (ValueError, TypeError):
                    pass

        table = f"\n## {day_name}\n\n"
        table += "| حرکت | عضله هدف | ست | تکرار | استراحت | تنفس و نکات |\n"
        table += "|------|----------|-----|--------|----------|-------------|\n"

        for exercise in exercises:
            # Get breathing instruction (use language)
            default_breathing = "دم هنگام پایین آوردن، بازدم هنگام بالا بردن" if language == 'fa' else "Breathe in on the way down, breathe out on the way up"
            breathing = (exercise.breathing_guide_fa if language == 'fa' else exercise.breathing_guide_en) or default_breathing

            # Add month-specific breathing emphasis
            if month == 1:
                breathing += ". تمرکز بر تنفس عمیق و کنترل شده"
            elif month <= 3:
                breathing += ". تنفس ریتمیک و هماهنگ"
            else:
                breathing += ". تنفس قدرتمند و کنترل شده"

            # Get form tips (execution_tips from exercise)
            default_tips = "فرم صحیح را حفظ کنید" if language == 'fa' else "Maintain proper form"
            form_tips = (exercise.execution_tips_fa if language == 'fa' else exercise.execution_tips_en) or default_tips

            # Combine breathing and tips
            breathing_tips = f"{breathing}. {form_tips}"
            
            ex_name = exercise.name_fa if language == 'fa' else (exercise.name_en or exercise.name_fa)
            ex_muscle = exercise.target_muscle_fa if language == 'fa' else (exercise.target_muscle_en or exercise.target_muscle_fa)
            table += f"| {ex_name} | {ex_muscle} | {sets} | {reps} | {rest_seconds}s | {breathing_tips} |\n"
        
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
        db = _db()
        recent_logs = db.session.query(WorkoutLog).filter_by(user_id=self.user_id)\
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
        exercise_pool: List[Exercise],
        language: str = "fa"
    ) -> Dict[str, Any]:
        """Handle workout plan request. Uses user profile + admin's Training Levels Info (Training Info tab)."""
        
        # Determine target muscle groups from message
        muscle_groups = self._extract_muscle_groups(message)
        
        # Get safe exercises
        if exercise_pool:
            safe_exercises = self.get_safe_exercises(exercise_pool, injuries)
        else:
            # Query exercises from database
            db = _db()
            query = db.session.query(Exercise)
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
        
        # Build training_levels_config from admin's Training Info (Training Levels Info)
        training_levels_config = self._get_training_levels_config(language)

        # Generate response
        response = f"## برنامه تمرینی - ماه {month}: {rules['name_fa']}\n\n"
        focus_text = rules['name_fa'] if language == 'fa' else rules.get('name_en', rules['name_fa'])
        if training_levels_config and training_levels_config.get('training_focus'):
            focus_text = training_levels_config['training_focus']
        response += f"**تمرکز این ماه:** {focus_text}\n\n"

        if injuries:
            response += f"✅ **بررسی ایمنی:** تمام تمرینات با در نظر گیری {', '.join(injuries)} شما انتخاب شده‌اند.\n\n"
            injury_notes = self._get_injury_important_notes(injuries, language)
            if injury_notes:
                response += f"**نکات مهم برای آسیب‌های شما:**\n{injury_notes}\n\n" if language == 'fa' else f"**Important notes for your injuries:**\n{injury_notes}\n\n"

        # Add workout table (uses admin's sets, reps, rest from Training Levels Info)
        response += self.format_workout_table_markdown(
            selected_exercises, month, language=language,
            training_levels_config=training_levels_config
        )
        
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
            exercise_pool = _db().session.query(Exercise).all()
        
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
        recent_progress = _db().session.query(ProgressEntry).filter_by(user_id=self.user_id)\
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

