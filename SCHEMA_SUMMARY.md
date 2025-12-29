# Database Schema Summary - Raha Fitness

## What Was Created

I've created a comprehensive database schema for your Persian fitness AI agent platform with full support for:

### ✅ Exercise Categories
1. **Bodybuilding – Machine** (`bodybuilding_machine`) - حرکات باشگاهی با دستگاه
2. **Functional – Home** (`functional_home`) - حرکات فانکشنال / بدون وسیله  
3. **Hybrid / HIIT + Machine** (`hybrid_hiit_machine`) - حرکات ترکیبی

### ✅ Exercise Schema Fields
Each exercise includes:
- ✅ Name (Persian & English)
- ✅ Target Muscle (Persian & English) - عضله درگیر
- ✅ Level (Beginner/Intermediate/Advanced)
- ✅ Execution Tips (Persian & English) - نکات اجرا
- ✅ Breathing Guide (Persian & English) - دم و بازدم
- ✅ Gender Suitability (Male/Female/Both)
- ✅ Injury Contraindications (JSON array)
- ✅ Intensity Level (Light/Medium/Heavy)

### ✅ User Profile Schema
Includes:
- ✅ Age, weight, height
- ✅ Training level
- ✅ Fitness goals (JSON array)
- ✅ Injuries (JSON array)
- ✅ Equipment access (JSON array)
- ✅ Workout history (via ExerciseHistory)
- ✅ Preferences (workout time, days per week, intensity)

### ✅ UTF-8 Support
All string fields support UTF-8 encoding for proper Persian text storage and retrieval.

## Files Created

1. **`prisma/schema.prisma`** - Prisma schema (TypeScript/Node.js compatible)
2. **`backend/models.py`** - SQLAlchemy models (Python/Flask compatible)
3. **`database_schema.sql`** - Raw SQL schema (database-agnostic)
4. **`database_schema.md`** - Comprehensive documentation
5. **`backend/seed_exercises.py`** - Sample exercise data seeder
6. **`SCHEMA_MIGRATION.md`** - Migration guide from old to new schema

## Quick Start

### Using Prisma (TypeScript/Node.js)

```bash
# Install Prisma
npm install prisma @prisma/client

# Generate Prisma Client
npx prisma generate

# Create database
npx prisma db push
```

### Using SQLAlchemy (Python/Flask)

```python
from models import Exercise, UserProfile, ExerciseHistory
from app import db

# Create tables
db.create_all()

# Seed exercises
python backend/seed_exercises.py
```

### Using Raw SQL

```bash
# SQLite
sqlite3 raha_fitness.db < database_schema.sql

# PostgreSQL
psql -d raha_fitness < database_schema.sql

# MySQL
mysql -u user -p raha_fitness < database_schema.sql
```

## Example Usage

### Create an Exercise

```python
from models import (
    Exercise, 
    EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
    TRAINING_LEVEL_INTERMEDIATE,
    INTENSITY_MEDIUM,
    GENDER_BOTH
)

exercise = Exercise(
    category=EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
    name_fa='پرس سینه با دستگاه',
    name_en='Chest Press Machine',
    target_muscle_fa='سینه، شانه، سه‌سر بازو',
    target_muscle_en='Chest, Shoulders, Triceps',
    level=TRAINING_LEVEL_INTERMEDIATE,
    intensity=INTENSITY_MEDIUM,
    execution_tips_fa='کمر را صاف نگه دارید...',
    execution_tips_en='Keep your back straight...',
    breathing_guide_fa='دم هنگام پایین آوردن...',
    breathing_guide_en='Inhale when lowering...',
    gender_suitability=GENDER_BOTH,
    injury_contraindications='["shoulder", "lower_back"]',
    equipment_needed_fa='دستگاه پرس سینه',
    equipment_needed_en='Chest Press Machine'
)
db.session.add(exercise)
db.session.commit()
```

### Create a User Profile

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
profile.set_fitness_goals(["muscle_gain", "strength"])
profile.set_injuries(["knee"])
profile.set_equipment_access(["machine", "dumbbells"])
db.session.add(profile)
db.session.commit()
```

### Query Exercises by Category

```python
from models import Exercise, EXERCISE_CATEGORY_FUNCTIONAL_HOME

# Get all home exercises
home_exercises = Exercise.query.filter_by(
    category=EXERCISE_CATEGORY_FUNCTIONAL_HOME
).all()

# Get exercises suitable for user's level and injuries
user_profile = UserProfile.query.filter_by(user_id=user_id).first()
user_injuries = user_profile.get_injuries()

# Filter out exercises with contraindications
safe_exercises = Exercise.query.filter(
    Exercise.level == user_profile.training_level,
    ~Exercise.injury_contraindications.contains(injury) for injury in user_injuries
).all()
```

## Schema Features

### Bilingual Support
All user-facing text fields have both Persian (`_fa`) and English (`_en`) versions.

### JSON Fields
UserProfile uses JSON for arrays:
- `fitness_goals` - List of fitness objectives
- `injuries` - List of injury types
- `equipment_access` - List of available equipment
- `home_equipment` - List of home equipment

Helper methods are provided for easy JSON handling:
- `get_fitness_goals()` / `set_fitness_goals()`
- `get_injuries()` / `set_injuries()`
- `get_equipment_access()` / `set_equipment_access()`

### Exercise Library vs History
- **Exercise** - Master library of all available exercises
- **ExerciseHistory** - User's completed workout sessions (can reference Exercise or be custom)

### Injury Safety
Exercises include `injury_contraindications` to help the AI agent filter out unsafe exercises based on user's injury profile.

## Next Steps

1. **Seed Exercise Library**: Run `python backend/seed_exercises.py` to add sample exercises
2. **Update API Endpoints**: Create endpoints to query exercises by category, level, etc.
3. **AI Agent Integration**: Use the schema to filter exercises based on user profile
4. **Frontend Integration**: Display exercises with proper Persian/English support

## Support

For detailed documentation, see:
- `database_schema.md` - Full schema documentation
- `SCHEMA_MIGRATION.md` - Migration guide
- `prisma/schema.prisma` - Prisma schema reference
- `database_schema.sql` - SQL reference



