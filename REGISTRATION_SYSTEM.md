# Comprehensive Registration System

## Overview
The registration system now collects comprehensive user information during signup to enable personalized AI-generated fitness and nutrition plans.

## Registration Flow

### Step 1: Account Information
- Username
- Email
- Password
- Confirm Password

### Step 2: Basic Information
- **Age** (years)
- **Gender** (Male/Female/Other)
- **Height** (cm)
- **Weight** (kg)
- **Fitness Level** (Beginner/Intermediate/Advanced)
- **Exercise History** (years of experience)
- **Exercise History Description** (free text)

### Step 3: Training Goals
Users can select multiple goals:
- **Fat Loss** (چربی‌سوزی)
- **Shaping and Muscle Building** (فرم‌دهی و عضله‌سازی)
- **Strength** (قدرت)
- **Endurance** (استقامت)
- **Combined** (ترکیبی)

### Step 4: Limitations & Injuries
- **Injuries** (checkboxes):
  - Knee (زانو)
  - Shoulder (شانه)
  - Lower Back (کمر)
  - Neck (گردن)
  - Wrist (مچ دست)
  - Ankle (مچ پا)
- **Injury Details** (free text description)
- **Medical Conditions** (checkboxes):
  - Heart Disease (بیماری قلبی)
  - High Blood Pressure (فشار خون بالا)
  - Pregnancy (بارداری)
- **Medical Condition Details** (free text description)

### Step 5: Training Conditions
- **Gym Access** (yes/no)
- **Gym Equipment** (if gym access):
  - Machines (دستگاه)
  - Dumbbells (دمبل)
  - Barbell (هالتر)
  - Cable Machine (کابل)
- **Home Equipment** (if no gym access):
  - Dumbbells (دمبل)
  - Resistance Bands (باند مقاومتی)
  - Yoga Mat (تشک یوگا)
  - Body Weight Only (فقط وزن بدن)
- **Workout Days Per Week** (1-7)
- **Preferred Workout Time** (Morning/Afternoon/Evening)

## Database Schema Updates

### UserProfile Model
New fields added:
- `exercise_history_years` (Integer)
- `exercise_history_description` (Text)
- `medical_conditions` (Text, JSON array)
- `medical_condition_details` (Text)

### Helper Methods
- `get_medical_conditions()` - Parse medical conditions JSON
- `set_medical_conditions()` - Set medical conditions from list

## AI Coach Integration

The AI coach now uses all collected information:

1. **Safety First**: 
   - Filters exercises based on injuries
   - Considers medical conditions (heart disease, high blood pressure, pregnancy)
   - Adjusts intensity based on age and fitness level

2. **Personalization**:
   - Equipment availability determines exercise selection
   - Fitness goals influence workout focus
   - Training level affects exercise difficulty
   - Workout frequency and time preferences are considered

3. **Workout Plan Generation**:
   - Uses `get_exercise_selection_criteria()` which includes:
     - User injuries and medical conditions
     - Fitness goals
     - Age and gender
     - Equipment access
     - Training level

## Frontend Components

### RegistrationForm.js
Multi-step form component with:
- Progress indicator (5 steps)
- Form validation
- Persian/English support
- Responsive design

### LandingPage.js
Updated to:
- Show RegistrationForm when user clicks "Register"
- Keep simple login form for existing users

## API Endpoints

### POST /api/register
Accepts:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "language": "fa|en",
  "profile": {
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 75,
    "training_level": "beginner",
    "exercise_history_years": 2,
    "exercise_history_description": "text",
    "fitness_goals": ["weight_loss", "muscle_gain"],
    "injuries": ["knee"],
    "injury_details": "text",
    "medical_conditions": ["high_blood_pressure"],
    "medical_condition_details": "text",
    "gym_access": true,
    "equipment_access": ["machine", "dumbbells"],
    "home_equipment": [],
    "workout_days_per_week": 4,
    "preferred_workout_time": "morning"
  }
}
```

## Usage

1. User clicks "ثبت نام" (Register) on landing page
2. Multi-step form appears
3. User completes all 5 steps
4. Profile data is saved with user account
5. AI coach uses this data for all future recommendations

## Benefits

1. **Comprehensive Data Collection**: All necessary information gathered upfront
2. **Safety**: Medical conditions and injuries considered from day one
3. **Personalization**: Plans tailored to user's exact situation
4. **User Experience**: Clear, step-by-step process with progress indicator
5. **Bilingual Support**: Full Persian and English support



