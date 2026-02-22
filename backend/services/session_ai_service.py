"""
AI service for session adaptation (mood/body), session-end encouragement, and post-set feedback.
Uses the admin-configured AI provider (OpenAI, Anthropic, or Gemini) via services.ai_provider.
"""

import json
from typing import Dict, Any, List, Optional, Tuple


def _ai_chat(system: str, user: str, max_tokens: int = 800, db=None) -> Optional[str]:
    """Call the configured AI provider (from admin AI settings). Returns None if unavailable.
    Pass db to load settings from the given db (avoids current_app issues in purchase flow)."""
    try:
        from services.ai_provider import chat_completion
        return chat_completion(system, user, max_tokens=max_tokens, db=db)
    except Exception as e:
        print(f"session_ai_service AI chat error: {e}")
        import traceback
        traceback.print_exc()
    return None


def _inject_session_phases(session: Dict[str, Any], db) -> None:
    """Inject warming and cooldown from admin session_phases into the session (for template fallback only)."""
    try:
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        raw = (getattr(row, 'session_phases_json', None) or '').strip() if row else ''
        if not raw:
            return
        data = json.loads(raw)
        if data.get('warming'):
            session['warming'] = data['warming']
        if data.get('cooldown'):
            session['cooldown'] = data['cooldown']
    except Exception:
        pass


def _extract_json_object(text: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Extract a JSON object from AI output. Returns (dict, error_message)."""
    if not text or not isinstance(text, str):
        return None, "AI returned empty or non-string"
    cleaned = text.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        for p in parts:
            p = p.strip()
            if p.lower().startswith("json"):
                p = p[4:].lstrip()
            if p.startswith("{"):
                try:
                    obj = json.loads(p)
                    if isinstance(obj, dict):
                        return obj, None
                except json.JSONDecodeError:
                    pass
    start = cleaned.find("{")
    if start != -1:
        depth = 0
        for i, c in enumerate(cleaned[start:], start):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(cleaned[start : i + 1])
                        if isinstance(obj, dict):
                            return obj, None
                    except json.JSONDecodeError:
                        pass
                    break
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj, None
    except json.JSONDecodeError as e:
        return None, str(e)
    return None, "Not a valid JSON object"


def _generate_warming_cooldown_for_session(
    session: Dict[str, Any],
    language: str,
    db,
) -> bool:
    """
    Generate warming and cooldown for a session via AI. Mutates session in place.
    Returns True if successful.
    """
    lang_fa = language == 'fa'
    exercises = session.get('exercises') or []
    ex_names = [e.get('name_fa') or e.get('name_en') or '' for e in exercises[:6]]
    session_name = session.get('name_fa') or session.get('name_en') or ''
    ex_summary = ", ".join(ex_names) if ex_names else "general"
    system_fa = """تو مربی تناسب اندام هستی. برای یک جلسه تمرینی، گرم کردن و سرد کردن طراحی کن.
خروجی فقط یک JSON معتبر با ساختار:
{"warming": {"title_fa": "...", "title_en": "...", "steps": [{"title_fa": "...", "title_en": "...", "body_fa": "...", "body_en": "..."}]}, "cooldown": {"title_fa": "...", "title_en": "...", "steps": [{"title_fa": "...", "title_en": "...", "body_fa": "...", "body_en": "..."}]}}
هر phase حداقل 2 step داشته باشد. متناسب با حرکات جلسه باشد."""
    system_en = """You are a fitness coach. Design warming and cooldown for a training session.
Output only valid JSON:
{"warming": {"title_fa": "...", "title_en": "...", "steps": [{"title_fa": "...", "title_en": "...", "body_fa": "...", "body_en": "..."}]}, "cooldown": {"title_fa": "...", "title_en": "...", "steps": [{"title_fa": "...", "title_en": "...", "body_fa": "...", "body_en": "..."}]}}
Each phase must have at least 2 steps. Match the session's exercises."""
    user_msg = f"Session: {session_name}. Exercises: {ex_summary}"
    out = _ai_chat(system_fa if lang_fa else system_en, user_msg, max_tokens=1200, db=db)
    if not out:
        return False
    obj, err = _extract_json_object(out)
    if not obj:
        return False
    if obj.get('warming') and isinstance(obj['warming'], dict):
        session['warming'] = obj['warming']
    if obj.get('cooldown') and isinstance(obj['cooldown'], dict):
        session['cooldown'] = obj['cooldown']
    return True


def _extract_json_array(text: str) -> Tuple[Optional[List], Optional[str]]:
    """
    Extract a JSON array from AI output. Handles markdown code blocks, extra text, etc.
    Returns (sessions_list, error_message). error_message is set when extraction fails.
    """
    if not text or not isinstance(text, str):
        return None, "AI returned empty or non-string"
    cleaned = text.strip()
    # Strip markdown code block
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        for i, p in enumerate(parts):
            p = p.strip()
            if p.lower().startswith("json"):
                p = p[4:].lstrip()
            if p.startswith("["):
                try:
                    obj = json.loads(p)
                    if isinstance(obj, list) and len(obj) > 0:
                        return obj, None
                    return None, "JSON is empty array or not a list"
                except json.JSONDecodeError as e:
                    return None, f"JSON parse error in code block: {e}"
    # Try to find [...] in text
    start = cleaned.find("[")
    if start != -1:
        depth = 0
        for i, c in enumerate(cleaned[start:], start):
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(cleaned[start : i + 1])
                        if isinstance(obj, list) and len(obj) > 0:
                            return obj, None
                        return None, "Extracted JSON is empty or not a list"
                    except json.JSONDecodeError as e:
                        return None, f"JSON parse error: {e}"
    # Direct parse
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, list) and len(obj) > 0:
            return obj, None
        return None, "Parsed JSON is empty array or not a list"
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"


def adapt_session_by_mood(
    session_json: Dict[str, Any],
    mood_or_message: str,
    language: str = 'fa',
) -> Dict[str, Any]:
    """
    Adapt a session based on mood/body. ONLY sets and reps are changed.
    Movements, order, instructions, rest, and plan structure stay the same.
    - Tired/exhausted/not well: lighter (fewer sets, lower reps).
    - Full of energy: heavier (more sets or reps).
    - Normal: no change or minimal.
    Returns same structure with modified exercises (sets/reps only) + optional extra_advice.
    """
    lang_fa = language == 'fa'
    exercises_orig = (session_json.get('exercises') or []) if isinstance(session_json, dict) else []
    if not exercises_orig and isinstance(session_json, list):
        exercises_orig = session_json
    session_str = json.dumps({'exercises': exercises_orig}, ensure_ascii=False)
    system_fa = """تو یک مربی حرفه‌ای تناسب اندام هستی. بر اساس حال ورزشکار، فقط تعداد ست‌ها و تکرارها را تطبیق بده.
قوانین سخت:
- حرکات، ترتیب، name_fa، name_en، instructions، rest را عوض نکن. فقط sets و reps.
- خسته/افسرده/بدحال/exhausted: ست‌ها و تکرارها را کم کن (مثلاً ۱ ست کمتر، یا reps پایین‌تر مثل 8 به جای 10-12). یک extra_advice کوتاه آرامش به فارسی بنویس.
- پرانرژی/full of energy: ست یا تکرار را کمی بیشتر کن (۱ ست اضافه یا reps بالاتر). استاندارد بماند.
- معمولی/normal: بدون تغییر یا تغییر خیلی کم.
خروجی فقط JSON معتبر: {"exercises": [...], "extra_advice": "..."}. هر exercise همان ساختار با فقط sets و reps تغییر یافته."""
    system_en = """You are a professional fitness coach. Adapt the session based on the member's mood. ONLY change sets and reps.
Strict rules:
- Do NOT change exercises, order, name_fa, name_en, instructions, rest. Only sets and reps.
- Tired/depressed/exhausted/not well: reduce sets and reps (e.g. 1 set less, or lower reps like 8 instead of 10-12). Add short extra_advice for relaxation.
- Full of energy: slightly increase sets or reps (1 extra set or higher reps). Keep it standard.
- Normal: no change or minimal.
Output only valid JSON: {"exercises": [...], "extra_advice": "..."}. Each exercise same structure with only sets and reps modified."""
    system = system_fa if lang_fa else system_en
    user = mood_or_message if mood_or_message else ('وضعیت معمولی' if lang_fa else 'Normal')
    user_msg = f"Session JSON:\n{session_str}\n\nMood/body or message: {user}"
    out = _ai_chat(system, user_msg, max_tokens=2000)
    if out:
        try:
            if out.startswith('```'):
                out = out.split('```')[1]
                if out.strip().lower().startswith('json'):
                    out = out.strip()[4:].lstrip()
            parsed = json.loads(out.strip())
            if isinstance(parsed, dict) and 'exercises' in parsed:
                ex_list = parsed.get('exercises', [])
                if ex_list and len(ex_list) == len(exercises_orig):
                    # Ensure we keep all original fields, only overwrite sets/reps
                    result = []
                    for i, orig in enumerate(exercises_orig):
                        if i < len(ex_list) and isinstance(orig, dict) and isinstance(ex_list[i], dict):
                            merged = dict(orig)
                            if 'sets' in ex_list[i]:
                                merged['sets'] = ex_list[i]['sets']
                            if 'reps' in ex_list[i]:
                                merged['reps'] = ex_list[i]['reps']
                            result.append(merged)
                        else:
                            result.append(orig)
                    return {'exercises': result, 'extra_advice': parsed.get('extra_advice', '') or ''}
        except (json.JSONDecodeError, TypeError):
            pass
    # Fallback: apply standard rules without AI
    exercises = []
    for ex in exercises_orig:
        if isinstance(ex, dict):
            exercises.append(dict(ex))
        else:
            exercises.append(ex)
    mood_raw = (mood_or_message or '').strip()
    mood_lower = mood_raw.lower()
    mood_fa = mood_raw
    extra = ''
    is_tired = any(x in mood_fa for x in ('خسته', 'افسرد', 'بدحال', 'ضعیف')) or any(x in mood_lower for x in ('tired', 'depress', 'exhaust', 'not well', 'low'))
    is_energy = any(x in mood_fa for x in ('پرانرژی', 'انرژی', 'قوی')) or any(x in mood_lower for x in ('energy', 'full', 'strong'))
    def _adjust_reps(reps_val, delta: int):
        try:
            if isinstance(reps_val, (int, float)):
                return str(max(4, int(reps_val) + delta))
            if isinstance(reps_val, str) and '-' in reps_val:
                parts = [p.strip() for p in reps_val.split('-') if p.strip()]
                if len(parts) >= 2:
                    lo, hi = int(parts[0]), int(parts[-1])
                    return f"{max(4, lo + delta)}-{max(6, hi + delta)}"
                if parts:
                    return str(max(4, int(parts[0]) + delta))
            return reps_val
        except (ValueError, TypeError):
            return reps_val

    if is_tired:
        if lang_fa:
            extra = 'امروز با شدت کمتر تمرین کنید. بین ست‌ها استراحت کافی داشته باشید.'
        else:
            extra = 'Today train lighter. Take enough rest between sets.'
        for ex in exercises:
            if isinstance(ex, dict):
                ex['sets'] = max(1, (ex.get('sets') or 3) - 1)
                ex['reps'] = _adjust_reps(ex.get('reps', '10-12'), -2)
    elif is_energy:
        for ex in exercises:
            if isinstance(ex, dict):
                ex['sets'] = (ex.get('sets') or 3) + 1
                ex['reps'] = _adjust_reps(ex.get('reps', '10-12'), 2)
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


def _generate_single_session(
    user_id: int,
    program_id: int,
    session_index: int,
    previous_session: Optional[Dict[str, Any]],
    language: str,
    db,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Generate exactly 1 session at a given index. Uses previous_session for continuity.
    Returns single session dict or (None, error_message).
    """
    from models import UserProfile, Configuration, Exercise, TrainingProgram

    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    template = db.session.get(TrainingProgram, program_id)
    duration_weeks = (template.duration_weeks if template else 4) or 4
    training_level = (profile.training_level if profile else 'beginner').strip().lower()
    workout_days = profile.workout_days_per_week if profile and profile.workout_days_per_week else 3
    workout_days = max(2, min(6, int(workout_days) if workout_days else 3))

    # Build profile summary
    parts = []
    if profile:
        if profile.age:
            parts.append(f"age={profile.age}")
        if profile.weight:
            parts.append(f"weight={profile.weight}kg")
        if profile.gender:
            parts.append(f"gender={profile.gender}")
        if profile.training_level:
            parts.append(f"training_level={profile.training_level}")
        if profile.workout_days_per_week:
            parts.append(f"workout_days_per_week={profile.workout_days_per_week}")
        if profile.get_fitness_goals():
            parts.append("fitness_goals=" + ",".join(profile.get_fitness_goals()))
        if profile.get_injuries():
            parts.append("injuries=" + ",".join(profile.get_injuries()))
        if profile.gym_access is not None:
            parts.append(f"gym_access={profile.gym_access}")
    profile_summary = "; ".join(parts) if parts else "beginner, 3 days per week"

    # Map user fitness_goals to Configuration purpose key
    goals = profile.get_fitness_goals() if profile and hasattr(profile, 'get_fitness_goals') else []
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

    # Get admin's Training Info (Configuration)
    admin_training_info = ""
    try:
        config = db.session.query(Configuration).first()
        if config and config.training_levels:
            raw = json.loads(config.training_levels) if isinstance(config.training_levels, str) else config.training_levels
            level_data = raw.get(training_level) or raw.get('beginner') or {}
            purposes = level_data.get('purposes') or {}
            purpose_data = purposes.get(purpose) or purposes.get('gain_muscle') or {}
            admin_training_info = (
                f"Admin Training Level Config for {training_level}, purpose={purpose}: "
                f"sets_per_action={purpose_data.get('sets_per_action')}, "
                f"reps_per_action={purpose_data.get('reps_per_action')}, "
                f"break_between_sets={purpose_data.get('break_between_sets')}, "
                f"sessions_per_week={purpose_data.get('sessions_per_week')}, "
                f"training_focus_fa={purpose_data.get('training_focus_fa', '')}, "
                f"training_focus_en={purpose_data.get('training_focus_en', '')}"
            )
        if config and config.injuries:
            raw_inj = json.loads(config.injuries) if isinstance(config.injuries, str) else config.injuries
            user_injuries = profile.get_injuries() if profile and hasattr(profile, 'get_injuries') else []
            user_injuries = [x for x in (user_injuries or []) if x and not str(x).startswith('common_')]
            injury_labels = {
                'knee': ('زانو', 'Knee'), 'shoulder': ('شانه', 'Shoulder'),
                'lower_back': ('کمر', 'Lower back'), 'neck': ('گردن', 'Neck'),
                'wrist': ('مچ دست', 'Wrist'), 'ankle': ('مچ پا', 'Ankle'),
            }
            def _movement_text(m):
                if isinstance(m, dict):
                    return m.get('fa') or m.get('en') or ''
                return str(m) if m else ''
            for inj_key in user_injuries:
                val = (raw_inj or {}).get(inj_key) if isinstance(raw_inj, dict) else None
                if not isinstance(val, dict):
                    continue
                purposes_fa = (val.get('purposes_fa') or '')[:150]
                purposes_en = (val.get('purposes_en') or '')[:150]
                allowed = val.get('allowed_movements') or []
                forbidden = val.get('forbidden_movements') or []
                allowed_str = ", ".join(_movement_text(m) for m in allowed[:12] if m)
                forbidden_str = ", ".join(_movement_text(m) for m in forbidden[:12] if m)
                admin_training_info += (
                    f"\nInjury {inj_key}: purposes={purposes_fa}/{purposes_en}. "
                    f"ALLOWED movements (use these, include corrective where appropriate): {allowed_str or 'none'}. "
                    f"FORBIDDEN movements (NEVER use): {forbidden_str or 'none'}."
                )
    except Exception:
        pass

    # Get exercise library
    exercises = db.session.query(Exercise).order_by(Exercise.id).limit(80).all()
    if profile and profile.gym_access is False:
        exercises = [e for e in exercises if e.category and 'functional' in (e.category or '').lower()]
    if not exercises:
        exercises = db.session.query(Exercise).limit(50).all()
    exercise_list = []
    for ex in exercises:
        exercise_list.append(f"{ex.name_fa} / {ex.name_en} (target: {ex.target_muscle_fa or ex.target_muscle_en})")
    exercises_text = "\n".join(exercise_list[:50])

    # Compute week/day for the single session we're generating
    week = (session_index // workout_days) + 1
    day = (session_index % workout_days) + 1

    lang_fa = language == 'fa'
    prev_context = ""
    if previous_session:
        prev_summary = json.dumps({
            "week": previous_session.get("week"),
            "day": previous_session.get("day"),
            "name_fa": previous_session.get("name_fa", "")[:80],
            "name_en": previous_session.get("name_en", "")[:80],
            "exercises": [
                {"name_fa": e.get("name_fa", ""), "name_en": e.get("name_en", ""), "sets": e.get("sets"), "reps": e.get("reps")}
                for e in (previous_session.get("exercises") or [])[:8]
            ],
        }, ensure_ascii=False)
        prev_context = f"\n\nPrevious session (design current to progress from this):\n{prev_summary}"

    system_fa = f"""تو یک مربی حرفه‌ای تناسب اندام هستی. بر اساس اطلاعات عضو و تنظیمات ادمین، دقیقاً یک جلسه تمرینی طراحی کن.
قوانین:
- هدف اصلی عضو (purpose={purpose}) را رعایت کن. sets، reps، rest مطابق Admin Config.
- خروجی فقط یک آرایه JSON معتبر با دقیقاً ۱ جلسه باشد. جلسه: week={week}, day={day}، name_fa، name_en، exercises.
- هر exercise: name_fa, name_en, sets, reps, rest, instructions_fa, instructions_en.
- فقط از حرکات لیست Exercise Library استفاده کن. نام حرکت را دقیقاً از لیست کپی کن.
- سطح ({training_level})، اهداف و آسیب‌ها را رعایت کن.
- اگر عضو آسیب دارد: حرکات اصلاحی را در تمرین اصلی ادغام کن. فقط از حرکات ALLOWED استفاده کن. حرکات FORBIDDEN را هرگز استفاده نکن.
- بدون توضیح اضافه؛ فقط آرایه JSON با ۱ جلسه."""
    system_en = f"""You are a professional fitness coach. Based on member info and admin Training Info, design exactly 1 training session.
Rules:
- The member's primary purpose (purpose={purpose}) MUST drive the design. Use sets, reps, rest from Admin Config.
- Output only a valid JSON array with exactly 1 session. Session: week={week}, day={day}, name_fa, name_en, exercises.
- Each exercise: name_fa, name_en, sets, reps, rest, instructions_fa, instructions_en.
- Use ONLY exercises from the Exercise Library list. Copy exercise names exactly.
- Respect training level ({training_level}), fitness goals, and injuries.
- If member has injuries: merge corrective movements into the main training. Use ONLY ALLOWED movements. NEVER use FORBIDDEN movements.
- No extra text; only the JSON array with 1 session."""

    user_msg = f"""Member profile: {profile_summary}

Admin Training Info:
{admin_training_info}

Exercise Library (use only these - copy names exactly):
{exercises_text}{prev_context}"""

    out = _ai_chat(system_fa if lang_fa else system_en, user_msg, max_tokens=2500, db=db)
    if not out:
        from services.ai_provider import get_last_chat_error
        api_err = get_last_chat_error()
        msg = api_err if api_err else "AI provider returned no response"
        return None, msg
    sessions, parse_err = _extract_json_array(out)
    if sessions and isinstance(sessions, list) and len(sessions) >= 1:
        session = sessions[0]
        session["week"] = week
        session["day"] = day
        return session, ""
    raw_preview = (out[:300] + "...") if len(out) > 300 else out
    err = parse_err or "Unknown parse error"
    print(f"[_generate_single_session] AI output parse failed: {err}. Raw preview: {raw_preview}")
    return None, err


def generate_sessions_for_position(
    user_id: int,
    program_id: int,
    start_session_index: int,
    previous_session: Optional[Dict[str, Any]],
    language: str,
    db,
    count: int = 2,
) -> Tuple[Optional[List[Dict[str, Any]]], str]:
    """
    Generate 1 or 2 sessions at a given position. Flow to reduce AI limit:
    - Session 1 main training -> warming/cooldown for 1 -> Session 2 main training -> warming/cooldown for 2
    - Or for count=1: Session N main training -> warming/cooldown for N
    Returns list of session dicts or (None, error_message).
    """
    import time
    sessions_out = []
    prev = previous_session
    for i in range(count):
        idx = start_session_index + i
        sess, err = _generate_single_session(
            user_id=user_id,
            program_id=program_id,
            session_index=idx,
            previous_session=prev,
            language=language,
            db=db,
        )
        if not sess:
            return None, err
        # Generate warming/cooldown for this session (separate AI call)
        _generate_warming_cooldown_for_session(sess, language, db)
        sessions_out.append(sess)
        prev = sess
        if i == 0 and count > 1:
            time.sleep(2)
    return sessions_out, ""


def generate_personalized_program_after_purchase(
    user_id: int,
    program_id: int,
    language: str,
    db,
) -> Tuple[Optional[List[Dict[str, Any]]], str]:
    """
    Generate the first 2 sessions of a personalized program after purchase.
    Uses generate_sessions_for_position with start_session_index=0 (no previous session).
    Returns list of 2 session dicts or (None, error_message).
    """
    return generate_sessions_for_position(
        user_id=user_id,
        program_id=program_id,
        start_session_index=0,
        previous_session=None,
        language=language,
        db=db,
    )
