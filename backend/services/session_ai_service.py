"""
AI service for session adaptation (mood/body), session-end encouragement, and post-set feedback.
Uses the admin-configured AI provider (OpenAI, Anthropic, or Gemini) via services.ai_provider.
"""

import json
from typing import Dict, Any, List, Optional


def _ai_chat(system: str, user: str) -> Optional[str]:
    """Call the configured AI provider (from admin AI settings). Returns None if unavailable."""
    try:
        from services.ai_provider import chat_completion
        return chat_completion(system, user, max_tokens=800)
    except Exception as e:
        print(f"session_ai_service AI chat error: {e}")
    return None


def adapt_session_by_mood(
    session_json: Dict[str, Any],
    mood_or_message: str,
    language: str = 'fa',
) -> Dict[str, Any]:
    """
    Adapt a session (exercises) based on mood/body or free-text message.
    Keeps the same exercises (e.g. leg day stays leg day); adjusts sets/reps/difficulty.
    If mood suggests depression/tired, add short meditation/relaxation advice (as text).
    Returns the same structure with possibly modified exercises + optional extra_advice.
    """
    lang_fa = language == 'fa'
    session_str = json.dumps(session_json, ensure_ascii=False)
    system_fa = """تو یک مربی حرفه‌ای تناسب اندام هستی. بر اساس حال و وضعیت بدن ورزشکار، همان جلسه تمرینی را تطبیق بده.
قوانین: لیست حرکات و ترتیب آن‌ها را عوض نکن (مثلاً اگر روز پا است همان روز پا بماند). فقط تعداد ست‌ها، تکرارها، استراحت یا شدت را تغییر بده.
اگر ورزشکار خسته یا افسرده است: شدت را کم کن، استراحت بیشتر بده، و یک پاراگراف کوتاه مشاوره آرامش/مدیتیشن به زبان فارسی اضافه کن.
اگر پرانرژی است: می‌توانی ست یا تکرار را کمی بیشتر کنی.
خروجی را فقط به صورت یک آبجکت JSON معتبر بده با کلیدهای: exercises (آرایه همان ساختار حرکات با فیلدهای به‌روز شده)، extra_advice (متن مشاوره اضافه یا رشته خالی). بدون توضیح اضافه."""
    system_en = """You are a professional fitness coach. Adapt the given workout session based on the member's mood/body or message.
Rules: Do not change the list or order of exercises (e.g. if it's leg day keep it leg day). Only adjust sets, reps, rest or intensity.
If member is tired or depressed: reduce intensity, add more rest, and add a short paragraph of relaxation/meditation advice in English.
If full of energy: you may slightly increase sets or reps.
Output only a valid JSON object with keys: exercises (array of same structure with updated fields), extra_advice (string or empty). No extra text."""
    system = system_fa if lang_fa else system_en
    user = mood_or_message if mood_or_message else ( 'وضعیت معمولی' if lang_fa else 'Normal' )
    user_msg = f"Session JSON:\n{session_str}\n\nMood/body or message: {user}"
    out = _ai_chat(system, user_msg)
    if out:
        try:
            # Strip markdown code block if present
            if out.startswith('```'):
                out = out.split('```')[1]
                if out.startswith('json'):
                    out = out[4:]
            return json.loads(out.strip())
        except json.JSONDecodeError:
            pass
    # Fallback: return original session with optional extra_advice
    exercises = (session_json.get('exercises') or []) if isinstance(session_json, dict) else []
    if not exercises and isinstance(session_json, list):
        exercises = session_json
    mood_lower = (mood_or_message or '').lower()
    extra = ''
    if lang_fa:
        if 'خسته' in mood_or_message or 'تired' in mood_lower or 'افسرد' in mood_or_message or 'depress' in mood_lower:
            extra = 'امروز با شدت کمتر تمرین کنید و بین ست‌ها استراحت کافی داشته باشید. یک دقیقه نفس عمیق و آرامش می‌تواند به بازیابی کمک کند.'
        elif 'پرانرژی' in mood_or_message or 'انرژی' in mood_or_message or 'energy' in mood_lower:
            for ex in exercises:
                if isinstance(ex, dict):
                    ex['sets'] = ex.get('sets', 3) + 1
                    if 'reps' in ex and isinstance(ex['reps'], str) and '-' in ex['reps']:
                        ex['reps'] = ex['reps'].split('-')[-1].strip()
    else:
        if 'tired' in mood_lower or 'depress' in mood_lower:
            extra = 'Today train at lower intensity and take enough rest between sets. A minute of deep breathing can help recovery.'
        elif 'energy' in mood_lower or 'full' in mood_lower:
            for ex in exercises:
                if isinstance(ex, dict):
                    ex['sets'] = ex.get('sets', 3) + 1
    return {'exercises': exercises, 'extra_advice': extra}


def get_session_end_encouragement(language: str = 'fa', session_name: str = '') -> str:
    """Generate a short encouraging message when the member finishes a session."""
    lang_fa = language == 'fa'
    system_fa = "تو یک مربی انگیزشی هستی. یک پیام کوتاه و تشویق‌کننده (۲ تا ۳ جمله) به فارسی برای ورزشکاری که جلسه تمرینش را تمام کرده بنویس. از اموجی مناسب استفاده کن."
    system_en = "You are a motivational coach. Write a short encouraging message (2-3 sentences) in English for a member who just finished their workout session. Use appropriate emojis."
    user = f"Session: {session_name}" if session_name else ""
    out = _ai_chat(system_fa if lang_fa else system_en, user or 'Workout completed.')
    if out:
        return out
    if lang_fa:
        return "عالی! جلسه امروز را با موفقیت به پایان رساندید. 💪 استراحت و تغذیه خوب را فراموش نکنید."
    return "Great job! You've completed today's session. 💪 Don't forget rest and good nutrition."


def get_post_set_feedback(
    exercise_name_fa: str,
    exercise_name_en: str,
    user_answers: Dict[str, Any],
    target_muscle: str,
    language: str = 'fa',
) -> str:
    """
    Generate AI feedback based on member's post-set answers (how was it? which muscle? etc.).
    If they were correct, encourage; if not, correct gently.
    """
    lang_fa = language == 'fa'
    answers_str = json.dumps(user_answers, ensure_ascii=False)
    system_fa = """تو مربی تناسب اندام هستی. ورزشکار بعد از انجام یک ست به سوالاتی جواب داده (چه حسی داشت؟ سخت بود؟ کدام عضله تحت فشار بود؟).
بر اساس پاسخ‌ها: اگر درست گفته تشویق کن؛ اگر عضله درگیر را اشتباه گفته یا فرم را رعایت نکرده، با لحن دوستانه اصلاح کن و نکته کوتاه بده.
خروجی: فقط یک پاراگراف کوتاه (۲ تا ۴ جمله) به فارسی. بدون عنوان."""
    system_en = """You are a fitness coach. The member answered questions after a set (how did it feel? was it hard? which muscle was under pressure?).
Based on answers: if correct, encourage; if they got the target muscle wrong or form tip wrong, gently correct and give a short tip.
Output: only one short paragraph (2-4 sentences) in English. No title."""
    user = f"Exercise: {exercise_name_fa} / {exercise_name_en}. Target muscle: {target_muscle}. Answers: {answers_str}"
    out = _ai_chat(system_fa if lang_fa else system_en, user)
    if out:
        return out
    if lang_fa:
        return "ست شما خوب بود. به عضله هدف و فرم اجرا توجه کنید و در ست‌های بعدی همان را حفظ کنید."
    return "That set looked good. Keep focus on the target muscle and form for the next sets."


def generate_trial_week_program(profile_summary: str, language: str = 'fa') -> Optional[List[Dict[str, Any]]]:
    """
    Generate a 1-week (7-day) training program as a list of sessions based on member profile summary.
    Returns list of session dicts: [{ "week": 1, "day": 1, "name_fa", "name_en", "exercises": [...] }, ...].
    Each exercise: name_fa, name_en, sets, reps, rest, instructions_fa, instructions_en.
    """
    lang_fa = language == 'fa'
    system_fa = """تو یک مربی حرفه‌ای تناسب اندام هستی. بر اساس اطلاعات عضو، یک برنامه تمرینی ۱ هفته‌ای (فقط یک هفته) طراحی کن.
قوانین:
- خروجی فقط یک آرایه JSON معتبر از جلسات (sessions) باشد. هر جلسه: week (همیشه 1), day (1 تا 5)، name_fa، name_en، exercises.
- هر exercise: name_fa, name_en, sets (عدد), reps (رشته مثل "10-12"), rest (مثل "60 seconds"), instructions_fa, instructions_en.
- تعداد جلسات را بر اساس workout_days_per_week تنظیم کن (۳ تا ۵ جلسه برای هفته). اگر مشخص نیست ۳ جلسه بگذار.
- سطح (beginner/intermediate/advanced)، هدف، و محدودیت‌ها (injuries) را رعایت کن.
- بدون توضیح اضافه؛ فقط آرایه JSON."""
    system_en = """You are a professional fitness coach. Based on the member info, design a 1-week training program (one week only).
Rules:
- Output only a valid JSON array of sessions. Each session: week (always 1), day (1 to 5), name_fa, name_en, exercises.
- Each exercise: name_fa, name_en, sets (number), reps (string e.g. "10-12"), rest (e.g. "60 seconds"), instructions_fa, instructions_en.
- Number of sessions per week: 3 to 5 based on workout_days_per_week. If unknown use 3.
- Respect training level (beginner/intermediate/advanced), goals, and injuries.
- No extra text; only the JSON array."""
    user_msg = f"Member profile summary:\n{profile_summary}"
    out = _ai_chat(system_fa if lang_fa else system_en, user_msg)
    if not out:
        return None
    try:
        if out.startswith('```'):
            out = out.split('```')[1]
            if out.lstrip().startswith('json'):
                out = out.lstrip()[4:]
        sessions = json.loads(out.strip())
        if isinstance(sessions, list) and len(sessions) > 0:
            return sessions
    except json.JSONDecodeError:
        pass
    return None
