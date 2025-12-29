# Database Schema Documentation - Raha Fitness

## Overview

This document describes the database schema for the Raha Fitness platform, designed to support Persian (Farsi) and English text with full UTF-8 encoding.

## Exercise Categories

The platform supports three main exercise categories:

1. **Bodybuilding – Machine** (`bodybuilding_machine`) - حرکات باشگاهی با دستگاه
2. **Functional – Home** (`functional_home`) - حرکات فانکشنال / بدون وسیله
3. **Hybrid / HIIT + Machine** (`hybrid_hiit_machine`) - حرکات ترکیبی

## Core Models

### User
Basic user authentication and account information.

**Fields:**
- `id` (Integer, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `password_hash` (String)
- `language` (String, Default: 'fa') - 'fa' for Farsi, 'en' for English
- `created_at` (DateTime)

### UserProfile
Comprehensive user fitness profile with detailed information.

**Fields:**
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key → User, Unique)
- `age` (Integer, Optional)
- `weight` (Float, Optional) - in kg
- `height` (Float, Optional) - in cm
- `gender` (String, Optional) - 'male', 'female', 'other'
- `training_level` (String, Optional) - 'beginner', 'intermediate', 'advanced'
- `fitness_goals` (Text, JSON) - Array of goals: ["weight_loss", "muscle_gain", "endurance", etc.]
- `injuries` (Text, JSON) - Array of injury types: ["knee", "shoulder", "lower_back", etc.]
- `injury_details` (Text, Optional) - Detailed description
- `equipment_access` (Text, JSON) - Array: ["machine", "dumbbells", "barbell", "home", etc.]
- `gym_access` (Boolean, Default: false)
- `home_equipment` (Text, JSON) - Array of available home equipment
- `preferred_workout_time` (String, Optional) - 'morning', 'afternoon', 'evening'
- `workout_days_per_week` (Integer, Optional) - 1-7
- `preferred_intensity` (String, Optional) - 'light', 'medium', 'heavy'
- `updated_at` (DateTime)

**Helper Methods:**
- `get_fitness_goals()` - Returns list of fitness goals
- `set_fitness_goals(goals_list)` - Sets fitness goals from list
- `get_injuries()` - Returns list of injuries
- `set_injuries(injuries_list)` - Sets injuries from list
- `get_equipment_access()` - Returns list of equipment
- `set_equipment_access(equipment_list)` - Sets equipment from list
- `get_home_equipment()` - Returns list of home equipment
- `set_home_equipment(equipment_list)` - Sets home equipment from list

### Exercise
Comprehensive exercise library with Persian/English support.

**Fields:**
- `id` (Integer, Primary Key)
- `category` (String) - Exercise category
- `name_fa` (String) - نام فارسی (Persian name)
- `name_en` (String) - English name
- `target_muscle_fa` (String) - عضله درگیر (Persian)
- `target_muscle_en` (String) - Target Muscle (English)
- `level` (String) - 'beginner', 'intermediate', 'advanced'
- `intensity` (String) - 'light', 'medium', 'heavy'
- `execution_tips_fa` (Text, Optional) - نکات اجرا (Persian)
- `execution_tips_en` (Text, Optional) - Execution Tips (English)
- `breathing_guide_fa` (Text, Optional) - دم و بازدم (Persian)
- `breathing_guide_en` (Text, Optional) - Breathing Guide (English)
- `gender_suitability` (String) - 'male', 'female', 'both'
- `injury_contraindications` (Text, JSON) - Array: ["knee", "shoulder", "lower_back", etc.]
- `equipment_needed_fa` (String, Optional) - تجهیزات مورد نیاز (Persian)
- `equipment_needed_en` (String, Optional) - Equipment Needed (English)
- `video_url` (String, Optional)
- `image_url` (String, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Helper Methods:**
- `get_injury_contraindications()` - Returns list of contraindicated injuries
- `set_injury_contraindications(injuries_list)` - Sets contraindications from list
- `to_dict(language='fa')` - Converts exercise to dictionary based on language preference

### ExerciseHistory
Tracks user's completed exercises and workout sessions.

**Fields:**
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key → User)
- `exercise_id` (Integer, Foreign Key → Exercise, Optional) - Null for custom exercises
- `exercise_name_fa` (String, Optional) - For custom exercises
- `exercise_name_en` (String, Optional) - For custom exercises
- `category` (String, Optional)
- `sets` (Integer, Optional)
- `reps` (Integer, Optional)
- `weight` (Float, Optional) - in kg
- `duration` (Integer, Optional) - in minutes (for cardio/HIIT)
- `distance` (Float, Optional) - in km (for running, cycling, etc.)
- `calories_burned` (Integer, Optional)
- `notes_fa` (Text, Optional)
- `notes_en` (Text, Optional)
- `workout_date` (DateTime)
- `created_at` (DateTime)

**Indexes:**
- Composite index on `(user_id, workout_date)` for efficient querying

## Supporting Models

### ChatHistory
Stores AI assistant conversation history.

### NutritionPlan
Stores user nutrition plans (2-week and 4-week).

### Tip
Fitness tips and suggestions (bilingual).

### Injury
Injury information and prevention (bilingual).

## UTF-8 Support

All text fields support UTF-8 encoding to properly store and retrieve Persian (Farsi) characters. When using SQLite, ensure the database connection uses UTF-8 encoding. For PostgreSQL or MySQL, use UTF-8 collation.

## Example Usage

### Creating an Exercise

```python
from models import Exercise, EXERCISE_CATEGORY_BODYBUILDING_MACHINE, TRAINING_LEVEL_INTERMEDIATE, INTENSITY_MEDIUM, GENDER_BOTH

exercise = Exercise(
    category=EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
    name_fa='پرس سینه با دستگاه',
    name_en='Chest Press Machine',
    target_muscle_fa='سینه، شانه، سه‌سر بازو',
    target_muscle_en='Chest, Shoulders, Triceps',
    level=TRAINING_LEVEL_INTERMEDIATE,
    intensity=INTENSITY_MEDIUM,
    execution_tips_fa='کمر را صاف نگه دارید و به آرامی وزنه را پایین بیاورید.',
    execution_tips_en='Keep your back straight and slowly lower the weight.',
    breathing_guide_fa='دم هنگام پایین آوردن، بازدم هنگام بالا بردن',
    breathing_guide_en='Inhale when lowering, exhale when pushing up',
    gender_suitability=GENDER_BOTH,
    injury_contraindications='["shoulder", "lower_back"]',
    equipment_needed_fa='دستگاه پرس سینه',
    equipment_needed_en='Chest Press Machine'
)
```

### Creating a User Profile

```python
from models import UserProfile

profile = UserProfile(
    user_id=user.id,
    age=30,
    weight=75.5,
    height=175.0,
    gender='male',
    training_level='intermediate',
    fitness_goals='["muscle_gain", "strength"]',
    injuries='["knee"]',
    equipment_access='["machine", "dumbbells"]',
    gym_access=True,
    workout_days_per_week=4,
    preferred_intensity='medium'
)
```

## Migration Notes

If migrating from the old schema:
1. The old `Exercise` model is now `ExerciseHistory`
2. A new `Exercise` model represents the exercise library
3. A new `UserProfile` model stores detailed user information
4. All relationships have been updated accordingly



