"""
Adaptive Feedback System - Finds alternative exercises when user reports difficulty or pain
"""

from typing import List, Dict, Any, Optional
from app import db
from models import Exercise, UserProfile
from models_workout_log import WorkoutLog
import json

# Import vector search (if available)
try:
    from services.vectorSearchHelpers import searchExercisesWithProfile
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False

class AdaptiveFeedbackService:
    """Service for adaptive exercise recommendations based on user feedback"""
    
    def __init__(self, user_id: int, language: str = 'fa'):
        self.user_id = user_id
        self.language = language
        self.user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    def find_alternative_exercise(
        self,
        original_exercise: Exercise,
        reason: str,  # 'too_difficult' or 'pain'
        pain_location: Optional[str] = None
    ) -> Optional[Exercise]:
        """
        Find alternative exercise using vector search
        - Lower intensity for same muscle group
        - Different movement pattern
        - Avoids pain location
        """
        
        # Get target muscle groups
        target_muscles = original_exercise.target_muscle_en.split(',')
        primary_muscle = target_muscles[0].strip().lower()
        
        # Build search query
        if self.language == 'fa':
            if reason == 'too_difficult':
                query = f"تمرینات {original_exercise.target_muscle_fa} آسان‌تر"
            else:
                query = f"تمرینات {original_exercise.target_muscle_fa} جایگزین"
        else:
            if reason == 'too_difficult':
                query = f"easier {primary_muscle} exercises"
            else:
                query = f"alternative {primary_muscle} exercises"
        
        # Determine intensity filter
        intensity_order = ['light', 'medium', 'heavy']
        current_intensity = original_exercise.intensity
        current_idx = intensity_order.index(current_intensity)
        
        # For too_difficult, find lower intensity
        # For pain, find different movement pattern (same or lower intensity)
        if reason == 'too_difficult' and current_idx > 0:
            target_intensity = intensity_order[current_idx - 1]
        else:
            target_intensity = current_intensity  # Can be same or lower
        
        # Get user profile for filtering
        user_profile_dict = {
            'gym_access': self.user_profile.gym_access if self.user_profile else False,
            'equipment_access': self.user_profile.get_equipment_access() if self.user_profile else [],
            'injuries': self.user_profile.get_injuries() if self.user_profile else [],
            'training_level': self.user_profile.training_level if self.user_profile else 'beginner'
        }
        
        # Add pain location to injuries if provided
        if pain_location and reason == 'pain':
            if pain_location not in user_profile_dict['injuries']:
                user_profile_dict['injuries'].append(pain_location.lower())
        
        # Use vector search if available
        if VECTOR_SEARCH_AVAILABLE:
            try:
                from services.vectorSearchHelpers import searchExercisesWithProfile
                
                results = searchExercisesWithProfile(
                    query,
                    self.user_id,
                    {
                        'intensity': target_intensity,
                        'targetMuscle': primary_muscle,
                        'maxResults': 10,
                        'language': self.language
                    }
                )
                
                # Filter results to exclude original exercise and find best alternative
                for result in results:
                    if result.exercise_id != original_exercise.id:
                        # Check if different movement pattern (different category or name)
                        alt_exercise = Exercise.query.get(result.exercise_id)
                        if alt_exercise:
                            # Ensure it targets same muscle group
                            if primary_muscle in alt_exercise.target_muscle_en.lower():
                                return alt_exercise
            except Exception as e:
                print(f"Vector search error: {e}")
        
        # Fallback: Database query
        return self._find_alternative_db(original_exercise, reason, pain_location, target_intensity)
    
    def _find_alternative_db(
        self,
        original_exercise: Exercise,
        reason: str,
        pain_location: Optional[str],
        target_intensity: str
    ) -> Optional[Exercise]:
        """Fallback database query for alternatives"""
        
        # Get target muscles
        target_muscles = [m.strip().lower() for m in original_exercise.target_muscle_en.split(',')]
        primary_muscle = target_muscles[0]
        
        # Build query
        query = Exercise.query.filter(
            Exercise.id != original_exercise.id,
            Exercise.intensity == target_intensity
        )
        
        # Filter by equipment
        if self.user_profile and not self.user_profile.gym_access:
            query = query.filter(Exercise.category == 'functional_home')
        
        # Filter by target muscle (must include primary muscle)
        # This is a simplified check - in production, use full-text search
        alternatives = query.all()
        
        # Filter by muscle group match
        for alt in alternatives:
            alt_muscles = [m.strip().lower() for m in alt.target_muscle_en.split(',')]
            if any(muscle in alt_muscles for muscle in target_muscles):
                # Check injury contraindications
                if pain_location:
                    contraindications = alt.get_injury_contraindications() if hasattr(alt, 'get_injury_contraindications') else []
                    if pain_location.lower() not in [c.lower() for c in contraindications]:
                        return alt
                else:
                    return alt
        
        return None
    
    def log_workout_with_feedback(
        self,
        exercise_id: int,
        sets_completed: int,
        reps_completed: int,
        difficulty_rating: str = None,
        pain_reported: bool = False,
        pain_location: str = None,
        form_rating: int = None,
        weight_kg: float = None,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Log workout and automatically find alternative if needed
        Returns workout log entry with alternative suggestion if applicable
        """
        
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return {'error': 'Exercise not found'}
        
        # Create workout log entry
        workout_log = WorkoutLog(
            user_id=self.user_id,
            exercise_id=exercise_id,
            exercise_name_fa=exercise.name_fa,
            exercise_name_en=exercise.name_en,
            sets_completed=sets_completed,
            reps_completed=reps_completed,
            weight_kg=weight_kg,
            difficulty_rating=difficulty_rating,
            pain_reported=pain_reported,
            pain_location=pain_location,
            form_rating=form_rating,
            notes_fa=notes if self.language == 'fa' else None,
            notes_en=notes if self.language == 'en' else None
        )
        
        # Check if alternative needed
        alternative_exercise = None
        alternative_reason = None
        
        if difficulty_rating == 'too_difficult' or pain_reported:
            reason = 'pain' if pain_reported else 'too_difficult'
            alternative_exercise = self.find_alternative_exercise(
                exercise,
                reason,
                pain_location
            )
            
            if alternative_exercise:
                workout_log.alternative_exercise_id = alternative_exercise.id
                if self.language == 'fa':
                    if reason == 'too_difficult':
                        workout_log.alternative_reason_fa = f"این تمرین برای شما سخت بود. پیشنهاد می‌کنیم تمرین جایگزین '{alternative_exercise.name_fa}' را امتحان کنید."
                    else:
                        workout_log.alternative_reason_fa = f"به دلیل درد در {pain_location or 'ناحیه مورد نظر'}، تمرین جایگزین '{alternative_exercise.name_fa}' پیشنهاد می‌شود."
                else:
                    if reason == 'too_difficult':
                        workout_log.alternative_reason_en = f"This exercise was too difficult. We suggest trying alternative '{alternative_exercise.name_en}'."
                    else:
                        workout_log.alternative_reason_en = f"Due to pain in {pain_location or 'target area'}, alternative exercise '{alternative_exercise.name_en}' is suggested."
        
        db.session.add(workout_log)
        db.session.commit()
        
        # Prepare response
        response = {
            'workout_log_id': workout_log.id,
            'exercise_name_fa': exercise.name_fa,
            'exercise_name_en': exercise.name_en,
            'sets_completed': sets_completed,
            'reps_completed': reps_completed
        }
        
        if alternative_exercise:
            response['alternative_suggested'] = True
            response['alternative_exercise'] = {
                'id': alternative_exercise.id,
                'name_fa': alternative_exercise.name_fa,
                'name_en': alternative_exercise.name_en,
                'target_muscle_fa': alternative_exercise.target_muscle_fa,
                'target_muscle_en': alternative_exercise.target_muscle_en,
                'intensity': alternative_exercise.intensity,
                'level': alternative_exercise.level,
                'reason_fa': workout_log.alternative_reason_fa,
                'reason_en': workout_log.alternative_reason_en
            }
        else:
            response['alternative_suggested'] = False
        
        return response

