# 6-Month Workout Plan Generator - Implementation Guide

## Overview

A complete logic controller for generating personalized 6-month workout plans with monthly progression rules, Persian fitness terminology, and JSON output formatted as weekly tables.

## Features

✅ **Monthly Progression Rules**
- Month 1: Form, control, and breathing (آموزش فرم و تنفس)
- Month 2: Increase repetitions and sets (افزایش تکرار و ست)
- Month 3: Hybrid and advanced movements (حرکات ترکیبی و پیشرفته)
- Month 4: Explosive movements (حرکات انفجاری)
- Month 5: Intensity and Supersets (افزایش شدت و سوپرست)
- Month 6: Stabilization and challenge (تثبیت و چالش)

✅ **Persian Fitness Terminology**
- All output includes professional Persian terms
- Bilingual support (Persian/English)

✅ **JSON Weekly Table Format**
- Exercise names (Persian & English)
- Sets and reps
- Breathing notes
- Form tips
- Rest periods

## Files Created

### Backend

1. **`backend/services/workout_plan_generator.py`**
   - Core logic for plan generation
   - Monthly progression rules
   - Exercise selection
   - Persian terminology mapping

2. **`backend/api/workout_plan_api.py`**
   - REST API endpoints
   - Plan generation endpoints
   - Month-specific generation

### Frontend

3. **`frontend/src/services/workoutPlanService.ts`**
   - TypeScript service for API calls
   - Type definitions

4. **`frontend/src/components/WorkoutPlanViewer.tsx`**
   - React component for viewing plans
   - Table and plan view modes
   - Month/week navigation

5. **`frontend/src/components/WorkoutPlanViewer.css`**
   - Styling for plan viewer

## Monthly Progression Rules

### Month 1: آموزش فرم و تنفس (Form and Breathing Training)
- **Focus**: Form, control, breathing
- **Sets**: 2-3
- **Reps**: 8-12
- **Rest**: 60 seconds
- **Intensity**: Light
- **Advanced/Hybrid/Explosive**: None
- **Supersets**: No

### Month 2: افزایش تکرار و ست (Increase Reps and Sets)
- **Focus**: Volume, endurance
- **Sets**: 3-4
- **Reps**: 12-15
- **Rest**: 60 seconds
- **Intensity**: Light
- **Advanced/Hybrid/Explosive**: None
- **Supersets**: No

### Month 3: حرکات ترکیبی و پیشرفته (Hybrid and Advanced Movements)
- **Focus**: Hybrid, progression
- **Sets**: 3-4
- **Reps**: 10-12
- **Rest**: 90 seconds
- **Intensity**: Medium
- **Advanced/Hybrid**: Yes
- **Explosive**: No
- **Supersets**: No

### Month 4: حرکات انفجاری (Explosive Movements)
- **Focus**: Explosive, power
- **Sets**: 3-4
- **Reps**: 8-10
- **Rest**: 120 seconds
- **Intensity**: Heavy
- **Advanced/Hybrid/Explosive**: Yes
- **Supersets**: No

### Month 5: افزایش شدت و سوپرست (Increase Intensity and Supersets)
- **Focus**: Intensity, supersets
- **Sets**: 4-5
- **Reps**: 8-12
- **Rest**: 60 seconds
- **Supersets**: Yes
- **Intensity**: Heavy

### Month 6: تثبیت و چالش (Stabilization and Challenge)
- **Focus**: Stabilization, challenge
- **Sets**: 4-5
- **Reps**: 10-15
- **Rest**: 90 seconds
- **Intensity**: Heavy
- **All features**: Enabled

## API Endpoints

### Generate 6-Month Plan
```http
POST /api/workout-plan/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "language": "fa"  // or "en"
}
```

**Response:**
```json
{
  "success": true,
  "plan": {
    "user_id": 1,
    "generated_at": "2024-01-01T00:00:00",
    "language": "fa",
    "total_duration_months": 6,
    "workout_days_per_week": 4,
    "months": {
      "month_1": {
        "month_number": 1,
        "month_name_fa": "آموزش فرم و تنفس",
        "weeks": {
          "week_1": {
            "week_number": 1,
            "days": {
              "day_1": {
                "day": 1,
                "exercises": [...]
              }
            }
          }
        }
      }
    }
  },
  "weekly_table": {
    "month_1_week_1": {
      "month": 1,
      "week": 1,
      "workouts": [...]
    }
  }
}
```

### Generate Single Month
```http
POST /api/workout-plan/generate-month
Authorization: Bearer <token>
Content-Type: application/json

{
  "month": 1,
  "language": "fa"
}
```

### Get Progression Rules
```http
GET /api/workout-plan/rules
```

## JSON Structure

### Weekly Table Format
```json
{
  "month_1_week_1": {
    "month": 1,
    "week": 1,
    "month_focus_fa": "آموزش فرم و تنفس",
    "month_focus_en": "Form and Breathing Training",
    "workouts": [
      {
        "day": 1,
        "workout_type_fa": "تمرین معمولی",
        "workout_type_en": "Regular Workout",
        "exercises": [
          {
            "exercise_name_fa": "پرس سینه با دستگاه",
            "exercise_name_en": "Chest Press Machine",
            "target_muscle_fa": "سینه، شانه، سه‌سر بازو",
            "sets": 3,
            "reps": 10,
            "rest_seconds": 60,
            "breathing_note_fa": "دم هنگام پایین آوردن، بازدم هنگام بالا بردن. تمرکز بر دم و بازدم عمیق و کنترل شده.",
            "form_tips_fa": "کمر را صاف نگه دارید و به آرامی وزنه را پایین بیاورید."
          }
        ],
        "supersets": [
          [
            {
              "exercise_name_fa": "پرس سینه",
              "sets": 4,
              "reps": 8,
              "breathing_note_fa": "..."
            },
            {
              "exercise_name_fa": "فلای سینه",
              "sets": 4,
              "reps": 8,
              "breathing_note_fa": "..."
            }
          ]
        ]
      }
    ]
  }
}
```

## Persian Terminology

All fitness terms are translated:

- **ست** (Sets)
- **تکرار** (Reps)
- **استراحت** (Rest)
- **دم** (Inhale)
- **بازدم** (Exhale)
- **فرم** (Form)
- **کنترل** (Control)
- **انفجاری** (Explosive)
- **سوپرست** (Superset)
- **شدت** (Intensity)
- **تثبیت** (Stabilization)
- **چالش** (Challenge)

## Usage Examples

### Backend (Python)
```python
from services.workout_plan_generator import WorkoutPlanGenerator
from models import Exercise

# Get exercise pool
exercise_pool = Exercise.query.filter_by(category='bodybuilding_machine').all()

# Generate plan
generator = WorkoutPlanGenerator(user_id=1, language='fa')
plan = generator.generate_6_month_plan(exercise_pool)
weekly_table = generator.format_plan_for_table(plan)
```

### Frontend (TypeScript)
```typescript
import { workoutPlanService } from './services/workoutPlanService';

// Generate full plan
const result = await workoutPlanService.generate6MonthPlan('fa');
console.log(result.weekly_table);

// Generate single month
const monthPlan = await workoutPlanService.generateMonthPlan(1, 'fa');
```

### React Component
```tsx
import WorkoutPlanViewer from './components/WorkoutPlanViewer';

<WorkoutPlanViewer userId={user.id} language="fa" />
```

## Exercise Selection Logic

1. **Equipment Filter**: Based on user's gym_access and equipment_access
2. **Level Filter**: Matches user's training_level
3. **Injury Filter**: Excludes exercises with matching injury contraindications
4. **Month Rules**: Applies monthly progression rules
5. **Muscle Group Split**: Rotates push/pull/legs/core/full-body

## Breathing Instructions

Each exercise includes detailed breathing notes:

- **Month 1**: "دم هنگام پایین آوردن، بازدم هنگام بالا بردن. تمرکز بر دم و بازدم عمیق و کنترل شده."
- **Month 2-3**: "دم هنگام پایین آوردن، بازدم هنگام بالا بردن. تنفس ریتمیک و هماهنگ با حرکت."
- **Month 4-6**: "دم هنگام پایین آوردن، بازدم هنگام بالا بردن. تنفس قدرتمند و کنترل شده."

## Supersets (Month 5-6)

Exercises are grouped into supersets:
- Pairs of exercises performed back-to-back
- Reduced rest between exercises
- Increased intensity

## Integration with AI Agent

The workout plan generator can be integrated with the AI agent:

```python
# In AI agent response
if 'برنامه تمرین' in user_message or 'workout plan' in user_message.lower():
    generator = WorkoutPlanGenerator(user_id, language)
    plan = generator.generate_6_month_plan(exercise_pool)
    return format_plan_response(plan)
```

## Next Steps

1. **Populate Exercise Database**: Ensure 200+ exercises per category
2. **Test Plan Generation**: Generate plans for different user profiles
3. **Integrate with AI**: Add plan generation to AI agent responses
4. **Add Progress Tracking**: Track user's progress through the plan
5. **Customization**: Allow users to modify plans based on preferences

## Notes

- Plans are personalized based on user profile
- Exercises are filtered by injuries (strict exclusion)
- Equipment availability is considered
- Monthly progression is automatic
- All output includes Persian terminology
- JSON format is optimized for table display



