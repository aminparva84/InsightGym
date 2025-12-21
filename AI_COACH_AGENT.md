# Persian Fitness Coach AI Agent

## Overview

Professional, empathetic Persian-speaking Fitness Coach AI that provides safe, personalized, and scientific workout plans using Vector Database integration.

## Key Features

✅ **Persian Language Communication**
- All responses in professional Persian (Farsi)
- Uses proper gym terminology
- Encouraging and motivating tone

✅ **Vector Database Integration**
- Retrieves exercises from Vector DB (no hallucination)
- Semantic search in Persian
- Filters by user profile

✅ **Safety First**
- Detects injuries in user messages
- Cross-checks 'Injury Contraindications' field
- Removes unsafe exercises automatically
- Provides safety warnings

✅ **6-Month Periodization**
- Follows monthly progression rules
- Month 1: Form and breathing (آموزش فرم و تنفس)
- Month 2: Increase reps and sets (افزایش تکرار و ست)
- Month 3: Hybrid movements (حرکات ترکیبی)
- Month 4: Explosive movements (حرکات انفجاری)
- Month 5: Intensity and supersets (افزایش شدت و سوپرست)
- Month 6: Stabilization and challenge (تثبیت و چالش)

✅ **Markdown Table Formatting**
- Clear workout tables
- Includes 'Breathing & Tips' column
- Professional presentation

## Operating Rules

1. **Language:** Always Persian (Farsi) with professional terminology
2. **Data Usage:** Vector DB only - no hallucinated exercises
3. **Safety First:** Cross-check injury contraindications
4. **Progression:** Follow 6-month periodization
5. **Formatting:** Markdown tables with breathing tips
6. **Tone:** Encouraging, like a personal trainer

## API Endpoints

### Chat with Coach
```http
POST /api/ai-coach/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "سلام، می‌خواهم یک برنامه تمرینی برای سینه داشته باشم"
}
```

**Response:**
```json
{
  "success": true,
  "response": "## برنامه تمرینی - ماه 1: آموزش فرم و تنفس\n\n...",
  "metadata": {
    "injuries_detected": [],
    "safety_checked": true,
    "exercises_suggested": [1, 2, 3],
    "month": 1
  }
}
```

### Generate Workout Plan
```http
POST /api/ai-coach/workout-plan
Authorization: Bearer <token>
Content-Type: application/json

{
  "month": 1,
  "target_muscle": "سینه",
  "language": "fa"
}
```

## Example Conversations

### Greeting
**User:** "سلام"
**Coach:** 
```
سلام! 👋

من مربی شخصی شما هستم و آماده‌ام تا یک برنامه تمرینی کاملاً شخصی‌سازی شده برای شما طراحی کنم.

چگونه می‌توانم به شما کمک کنم؟
- می‌خواهید یک برنامه تمرینی دریافت کنید؟
- سوالی در مورد تمرینات دارید؟
- می‌خواهید پیشرفت خود را بررسی کنید؟
```

### Workout Plan Request
**User:** "برنامه تمرینی برای سینه می‌خواهم"
**Coach:**
```markdown
## برنامه تمرینی - ماه 1: آموزش فرم و تنفس

**تمرکز این ماه:** آموزش فرم و تنفس

| حرکت | عضله هدف | ست | تکرار | استراحت | تنفس و نکات |
|------|----------|-----|--------|----------|-------------|
| پرس سینه با دستگاه | سینه، شانه، سه‌سر بازو | 3 | 12 | 60s | دم هنگام پایین آوردن، بازدم هنگام بالا بردن. تمرکز بر تنفس عمیق و کنترل شده. کمر را صاف نگه دارید... |
| فلای سینه | سینه | 3 | 12 | 60s | ... |

### نکات مهم:
- **گرم کردن:** قبل از شروع، ۵-۱۰ دقیقه گرم کردن انجام دهید
- **سرد کردن:** بعد از تمرین، ۵ دقیقه سرد کردن و کشش
- **فرم صحیح:** در ماه اول، تمرکز اصلی بر فرم و تکنیک است
```

### Injury Report
**User:** "کمردرد دارم"
**Coach:**
```
⚠️ **توجه به ایمنی شما:**

متوجه شدم که شما lower_back دارید. تمام تمرینات پیشنهادی من با بررسی دقیق ممنوعیت‌های آسیب (Injury Contraindications) انتخاب می‌شوند تا کاملاً ایمن باشند.

**توصیه‌های ایمنی:**
1. قبل از شروع هر برنامه تمرینی، با پزشک یا فیزیوتراپیست مشورت کنید
2. اگر در حین تمرین درد احساس کردید، فوراً متوقف کنید
3. من همیشه تمرینات جایگزین ایمن برای شما پیشنهاد می‌دهم

آیا می‌خواهید یک برنامه تمرینی ایمن برای شما طراحی کنم؟
```

## Safety Checks

### Injury Detection
The AI automatically detects injuries in Persian:
- کمردرد → lower_back
- زانو درد → knee
- شانه درد → shoulder
- etc.

### Contraindication Check
For each exercise:
1. Get `injury_contraindications` field
2. Compare with user's injuries
3. Exclude if match found
4. Only suggest safe exercises

## Integration

### With Vector Search
```python
from services.ai_coach_agent import PersianFitnessCoachAI

coach = PersianFitnessCoachAI(user_id)
response = coach.generate_personalized_response(
    "برنامه تمرینی می‌خواهم",
    exercise_pool  # From vector search
)
```

### With Workout Plan Generator
The AI coach uses the same monthly progression rules as the workout plan generator, ensuring consistency.

## Persian Terminology

- **گرم کردن** - Warm-up
- **سرد کردن** - Cool-down
- **ست** - Sets
- **تکرار** - Reps
- **استراحت** - Rest
- **دم/بازدم** - Inhale/Exhale
- **فرم** - Form
- **تکنیک** - Technique
- **شدت** - Intensity
- **پیشرفت** - Progression
- **جایگزین** - Alternative

## Next Steps

1. Integrate with chat interface
2. Add voice support (optional)
3. Enhance injury detection
4. Add more personalized recommendations
5. Track conversation history

