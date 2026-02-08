# Schema Migration Guide

## Overview

This guide explains how to migrate from the old schema to the new comprehensive schema that supports the exercise library and user profiles.

## Key Changes

### 1. Exercise Model Split

**Old Schema:**
- Single `Exercise` model for user exercise history

**New Schema:**
- `Exercise` - Exercise library (comprehensive exercise database)
- `ExerciseHistory` - User's completed exercises/workout sessions

### 2. New UserProfile Model

A new `UserProfile` model has been added to store detailed user fitness information.

### 3. Enhanced Exercise Fields

The new `Exercise` model includes:
- Persian and English names
- Target muscles (bilingual)
- Execution tips (bilingual)
- Breathing guides (bilingual)
- Injury contraindications
- Gender suitability
- Intensity levels
- Training levels

## Migration Steps

### Option 1: Fresh Start (Recommended for New Projects)

1. Backup existing database (if any)
2. Delete old database file
3. Update `app.py` to import models from `models.py`
4. Run the application to create new schema
5. Seed exercise library: `python backend/seed_exercises.py`

### Option 2: Migrate Existing Data

1. **Backup your database**
   - **PostgreSQL:** `pg_dump raha_fitness > raha_fitness_backup.sql`
   - **SQLite:** `cp raha_fitness.db raha_fitness_backup.db`

2. **Update app.py to use new models**
   - Replace inline model definitions with imports from `models.py`
   - Update relationships

3. **Create migration script** (see example below)

4. **Run migration**
   ```python
   python migrate_schema.py
   ```

5. **Verify data integrity**

## Example Migration Script

```python
"""
Migration script to update schema
Run this once to migrate from old to new schema
"""

from app import app, db
from sqlalchemy import text

def migrate_schema():
    with app.app_context():
        # Rename old exercises table to exercise_history
        try:
            db.session.execute(text("""
                ALTER TABLE exercise RENAME TO exercise_history_old
            """))
            
            # Create new tables
            db.create_all()
            
            # Migrate data from old exercise table
            db.session.execute(text("""
                INSERT INTO exercise_history (
                    user_id, exercise_name_fa, exercise_name_en,
                    duration, calories_burned, workout_date, notes_fa
                )
                SELECT 
                    user_id, 
                    exercise_name as exercise_name_fa,
                    exercise_name as exercise_name_en,
                    duration,
                    calories_burned,
                    date as workout_date,
                    notes as notes_fa
                FROM exercise_history_old
            """))
            
            # Drop old table
            db.session.execute(text("DROP TABLE exercise_history_old"))
            
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration error: {e}")
            raise

if __name__ == '__main__':
    migrate_schema()
```

## Updating app.py

Replace the model definitions in `app.py` with:

```python
from models import (
    User, UserProfile, Exercise, ExerciseHistory,
    ChatHistory, NutritionPlan, Tip, Injury
)
```

And remove the old inline model definitions.

## Testing the Migration

1. Verify all tables exist:
   ```python
   from app import db
   print(db.engine.table_names())
   ```

2. Check data integrity:
   ```python
   from models import User, ExerciseHistory, Exercise
   print(f"Users: {User.query.count()}")
   print(f"Exercise History: {ExerciseHistory.query.count()}")
   print(f"Exercise Library: {Exercise.query.count()}")
   ```

3. Test creating a new exercise:
   ```python
   from models import Exercise, EXERCISE_CATEGORY_BODYBUILDING_MACHINE
   exercise = Exercise(
       category=EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
       name_fa='تست',
       name_en='Test',
       target_muscle_fa='عضله تست',
       target_muscle_en='Test Muscle',
       level='beginner',
       intensity='light',
       gender_suitability='both'
   )
   db.session.add(exercise)
   db.session.commit()
   ```

## Rollback Plan

If migration fails:

1. Restore from backup:
   - **PostgreSQL:** `psql -d raha_fitness < raha_fitness_backup.sql`
   - **SQLite:** `cp raha_fitness_backup.db raha_fitness.db`

2. Revert `app.py` changes

3. Continue using old schema until issues are resolved

## Notes

- All text fields support UTF-8 for Persian characters
- JSON fields in UserProfile use `json.dumps()` and `json.loads()` for serialization
- The new schema is backward compatible with existing chat, nutrition, tips, and injuries data



