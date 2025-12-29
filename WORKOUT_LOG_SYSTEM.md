# Workout Log and Adaptive Feedback System

## Overview

Complete system for logging workouts, adaptive exercise recommendations, progress tracking, and goal setting with daily reminders.

## Features Implemented

✅ **Workout Logging**
- Log completed sets, reps, and weight
- Report difficulty level (too easy, just right, too difficult)
- Report pain with location
- Rate form level (1-5 scale)
- Add notes

✅ **Adaptive Feedback**
- Automatically finds alternative exercises when:
  - Exercise is "Too Difficult"
  - User reports "Pain"
- Uses Vector DB to find:
  - Lower intensity exercises
  - Different movement patterns
  - Same muscle group targeting
- Excludes exercises matching pain location

✅ **Progress Tracking**
- Weight tracking
- Body measurements (chest, waist, hips, arms, thighs)
- Form level over time
- Body fat percentage
- Muscle mass

✅ **Weekly Goals**
- Set workout days target
- Exercise-specific goals
- Weight/measurement targets
- Automatic progress tracking
- Completion percentage

✅ **Daily Reminders**
- Customizable reminder times
- Days of week selection
- Timezone support
- Persian/English messages

## Database Models

### WorkoutLog
- Tracks completed workouts
- Stores feedback (difficulty, pain, form)
- Links to alternative exercises when suggested

### ProgressEntry
- Weight and measurements
- Form level assessment
- Timestamped entries

### WeeklyGoal
- Weekly targets
- Progress tracking
- Status (active/completed/failed)

### WorkoutReminder
- Reminder settings
- Schedule configuration
- Next send time calculation

## API Endpoints

### Workout Logging
```http
POST /api/workout-log/log
{
  "exercise_id": 1,
  "sets_completed": 3,
  "reps_completed": 10,
  "weight_kg": 50,
  "difficulty_rating": "too_difficult",
  "pain_reported": false,
  "form_rating": 4,
  "notes": "..."
}
```

**Response with Alternative:**
```json
{
  "workout_log_id": 123,
  "alternative_suggested": true,
  "alternative_exercise": {
    "id": 45,
    "name_fa": "پرس سینه با دمبل",
    "name_en": "Dumbbell Chest Press",
    "target_muscle_fa": "سینه، شانه",
    "intensity": "medium",
    "level": "beginner",
    "reason_fa": "این تمرین برای شما سخت بود. پیشنهاد می‌کنیم تمرین جایگزین 'پرس سینه با دمبل' را امتحان کنید."
  }
}
```

### Progress Tracking
```http
POST /api/workout-log/progress
{
  "weight_kg": 75.5,
  "chest_cm": 100,
  "waist_cm": 85,
  "form_level": 4
}
```

### Weekly Goals
```http
POST /api/workout-log/goals
{
  "week_start_date": "2024-01-01",
  "workout_days_target": 4,
  "exercise_goals": [
    {"exercise_id": 1, "sets": 3, "reps": 10}
  ]
}
```

### Reminders
```http
POST /api/workout-log/reminders
{
  "reminder_time": "18:00",
  "days_of_week": [1, 2, 3, 4, 5],
  "message_fa": "زمان تمرین شما فرا رسیده است!"
}
```

## Adaptive Feedback Logic

### When Alternative is Suggested

1. **Too Difficult**
   - Finds lower intensity exercise
   - Same muscle group
   - Different movement pattern if available

2. **Pain Reported**
   - Excludes exercises with matching injury contraindications
   - Finds alternative movement pattern
   - Same or lower intensity
   - Avoids pain location

### Vector Search Integration

Uses vector search to find alternatives:
- Semantic search in Persian/English
- Filters by intensity, equipment, injuries
- Returns best matching alternatives

## Usage Examples

### Log Workout with Feedback
```typescript
import { workoutLogService } from './services/workoutLogService';

const result = await workoutLogService.logWorkout({
  exercise_id: 1,
  sets_completed: 3,
  reps_completed: 10,
  difficulty_rating: 'too_difficult',
  pain_reported: false,
  form_rating: 4
});

if (result.alternative_suggested) {
  console.log('Alternative:', result.alternative_exercise);
}
```

### Track Progress
```typescript
await workoutLogService.logProgress({
  weight_kg: 75.5,
  chest_cm: 100,
  waist_cm: 85,
  form_level: 4
});
```

### Create Weekly Goal
```typescript
await workoutLogService.createWeeklyGoal({
  week_start_date: '2024-01-01',
  workout_days_target: 4,
  exercise_goals: [
    { exercise_id: 1, sets: 3, reps: 10 }
  ]
});
```

## React Components

### WorkoutLogger
- Form for logging workouts
- Difficulty and pain reporting
- Form rating
- Displays alternative suggestions

### ProgressTracker (to be created)
- Weight/measurement input
- Progress charts
- Form level tracking

### GoalsManager (to be created)
- Create weekly goals
- Track progress
- View completion status

## Persian Terminology

- **ثبت تمرین** - Log Workout
- **ست** - Sets
- **تکرار** - Reps
- **سطح دشواری** - Difficulty Level
- **خیلی سخت** - Too Difficult
- **درد گزارش شده** - Pain Reported
- **سطح فرم** - Form Level
- **جایگزین** - Alternative
- **پیشنهاد جایگزین** - Alternative Suggestion

## Next Steps

1. Create ProgressTracker component
2. Create GoalsManager component
3. Implement reminder notification system
4. Add progress charts/visualizations
5. Integrate with AI agent for automatic suggestions



