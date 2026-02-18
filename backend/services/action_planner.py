"""
Action planner service for AI-driven actions with strict JSON output.
Uses current_app.extensions['sqlalchemy'] for db access to avoid Flask app context issues.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from app import User, TrainerMessage
from models import Exercise, UserProfile, SiteSettings, ProgressCheckRequest, TrainingProgram


def _db():
    """Get SQLAlchemy instance from current Flask app context."""
    return current_app.extensions['sqlalchemy']
from services.ai_provider import chat_completion
from services.website_kb import search_kb
from services.ai_coach_agent import PersianFitnessCoachAI


ALLOWED_ACTIONS = (
    'search_exercises',
    'create_workout_plan',
    'suggest_training_plans',
    'update_user_profile',
    'progress_check',
    'trainer_message',
    'site_settings',
    'schedule_meeting',
    'schedule_appointment',
)

ACTION_SPECS = {
    'search_exercises': {
        'required': [],
        'optional': ['query', 'target_muscle', 'level', 'intensity', 'max_results', 'language'],
    },
    'create_workout_plan': {
        'required': [],
        'optional': ['month', 'target_muscle', 'language'],
    },
    'suggest_training_plans': {
        'required': [],
        'optional': ['language', 'max_results'],
    },
    'update_user_profile': {
        'required': ['fields'],
        'optional': ['user_id'],
    },
    'progress_check': {
        'required': ['mode'],
        'optional': ['request_id', 'status'],
    },
    'trainer_message': {
        'required': ['body'],
        'optional': ['recipient_id'],
    },
    'site_settings': {
        'required': ['fields'],
        'optional': [],
    },
    'schedule_meeting': {
        'required': [],
        'optional': ['appointment_date', 'appointment_time', 'duration', 'notes', 'property_id'],
    },
    'schedule_appointment': {
        'required': [],
        'optional': ['appointment_date', 'appointment_time', 'duration', 'notes', 'property_id'],
    },
}

PROFILE_FIELDS_ALLOWED = {
    'age', 'weight', 'height', 'gender', 'training_level', 'fitness_goals',
    'injuries', 'equipment_access', 'gym_access', 'preferred_intensity',
    'workout_days_per_week', 'medical_conditions', 'home_equipment',
    'preferred_workout_time',
}

SITE_SETTINGS_FIELDS_ALLOWED = {
    'contact_email', 'contact_phone', 'address_fa', 'address_en',
    'app_description_fa', 'app_description_en', 'instagram_url', 'telegram_url',
    'whatsapp_url', 'twitter_url', 'facebook_url', 'linkedin_url', 'youtube_url',
    'copyright_text',
}


def _build_user_profile_summary(user: User) -> str:
    """Build a text summary of user profile for AI context."""
    db = _db()
    profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        return "No profile yet; assume beginner level, 3 days/week, gym_access=true."
    parts = []
    if profile.age:
        parts.append(f"age={profile.age}")
    if profile.gender:
        parts.append(f"gender={profile.gender}")
    if profile.training_level:
        parts.append(f"training_level={profile.training_level}")
    if profile.workout_days_per_week:
        parts.append(f"workout_days_per_week={profile.workout_days_per_week}")
    goals = profile.get_fitness_goals() if hasattr(profile, 'get_fitness_goals') else []
    if goals:
        parts.append(f"fitness_goals={','.join(goals)}")
    injuries = profile.get_injuries() if hasattr(profile, 'get_injuries') else []
    if injuries:
        parts.append(f"injuries={','.join(injuries)}")
    if profile.gym_access is not None:
        parts.append(f"gym_access={profile.gym_access}")
    if profile.equipment_access:
        parts.append(f"equipment_access={profile.equipment_access}")
    if profile.home_equipment:
        parts.append(f"home_equipment={profile.home_equipment}")
    return "; ".join(parts) if parts else "No profile details; assume beginner, gym_access=true."


def _build_prompt(message: str, language: str, role: str, user_profile_summary: str = "") -> Tuple[str, str]:
    system = (
        "You are an action planner for a fitness platform. "
        "Return ONLY valid JSON with keys: assistant_response (string) and actions (array). "
        "Each action must be an object with keys: action (string), params (object). "
        "Allowed actions: "
        "search_exercises, create_workout_plan, suggest_training_plans, update_user_profile, "
        "progress_check, trainer_message, site_settings, schedule_meeting, schedule_appointment. "
        "Do not include markdown or explanations. "
        "If no action is needed, return an empty actions array. "
        "IMPORTANT: Perform actions directly. Do NOT ask the user to confirm or clarify intent. "
        "suggest_training_plans: ALWAYS use when user wants to BUY or GET a training plan, or asks what plan to choose. Examples: 'میخوام برنامه تمرینی بخرم', 'چی پیشنهاد میدی؟', 'خرید برنامه', 'want to buy a program', 'what plan do you suggest'. Do NOT use create_workout_plan or search_exercises for buy/suggest requests. If user has not set fitness_goals in profile, the system will ask for their purpose (one of: weight_loss/کاهش وزن, muscle_gain/افزایش عضله, strength/قدرت, endurance/استقامت, flexibility/انعطاف‌پذیری). When user provides their goal in the same message, include update_user_profile with fields:{fitness_goals: ['muscle_gain']} before suggest_training_plans. Map: muscle gain/افزایش عضله->muscle_gain, weight loss/کاهش وزن->weight_loss, strength/قدرت->muscle_gain, endurance->endurance, flexibility->shape_fitting. "
        "create_workout_plan: ONLY when user has ALREADY bought a plan and asks to generate/build it (e.g. 'برنامه‌ام رو بساز', 'برنامه خریدم بساز', 'generate my workout'). Never use for 'میخوام برنامه بخرم' or 'what do you suggest'. "
        "When the user asks for exercises (e.g. 'تمرینات سینه', 'chest exercises'), use search_exercises with query or target_muscle. "
        "Only use respond (empty actions) when a required parameter is genuinely missing (e.g. recipient_id for trainer_message). "
        "For schedule_meeting/schedule_appointment: use relative date (e.g. tomorrow, in 2 days) and relative time (e.g. morning, afternoon, evening); the system will resolve them. Do NOT ask the user to specify exact date and time."
    )
    profile_block = f"\nUser profile (from KB/DB): {user_profile_summary}\n" if user_profile_summary else ""
    user = (
        f"UserRole: {role}\n"
        f"Language: {language}\n"
        f"Message: {message}\n"
        f"{profile_block}"
        "Action schemas:\n"
        "- search_exercises: params { query?, target_muscle?, level?, intensity?, max_results?, language? }\n"
        "- create_workout_plan: params { month?, target_muscle?, language? }\n"
        "- suggest_training_plans: params { language?, max_results? } - returns plans matched to user profile\n"
        "- update_user_profile: params { user_id?, fields (object) }\n"
        "- progress_check: params { mode ('request'|'respond'), request_id?, status? }\n"
        "- trainer_message: params { recipient_id?, body }\n"
        "- site_settings: params { fields (object) }\n"
        "- schedule_meeting / schedule_appointment: params { appointment_date?, appointment_time?, duration?, notes?, property_id? }\n"
        "Return JSON now."
    )
    return system, user


def _extract_json(text: str) -> Optional[str]:
    if not text or not isinstance(text, str):
        return None
    cleaned = text.strip()
    if cleaned.startswith('```'):
        parts = cleaned.split('```')
        if len(parts) >= 2:
            cleaned = parts[1]
            if cleaned.lstrip().startswith('json'):
                cleaned = cleaned.lstrip()[4:]
    # Try to find a JSON object in the text
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    return cleaned[start:end + 1]


def _normalize_actions(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    errors = []
    actions_raw = payload.get('actions')
    if actions_raw is None:
        return [], errors
    if not isinstance(actions_raw, list):
        return [], ['actions must be a list']
    actions: List[Dict[str, Any]] = []
    for idx, item in enumerate(actions_raw):
        if not isinstance(item, dict):
            errors.append(f'action[{idx}] must be object')
            continue
        action = (item.get('action') or '').strip()
        if action not in ALLOWED_ACTIONS:
            errors.append(f'action[{idx}] invalid action')
            continue
        params = item.get('params') or {}
        if not isinstance(params, dict):
            errors.append(f'action[{idx}].params must be object')
            continue
        spec = ACTION_SPECS.get(action, {})
        required = spec.get('required', [])
        for req in required:
            if req not in params:
                errors.append(f'action[{idx}] missing required param: {req}')
        allowed_keys = set(spec.get('required', []) + spec.get('optional', []))
        sanitized = {k: params[k] for k in params.keys() if k in allowed_keys}
        actions.append({'action': action, 'params': sanitized})
    return actions, errors


def plan_actions(message: str, user: User, language: str) -> Dict[str, Any]:
    profile_summary = _build_user_profile_summary(user)
    system, user_msg = _build_prompt(
        message, language, getattr(user, 'role', 'member') or 'member', profile_summary
    )
    kb_snippets = search_kb(message, top_k=3)
    if kb_snippets:
        snippet_texts = [f"- {s.get('text', '')}" for s in kb_snippets if s.get('text')]
        if snippet_texts:
            user_msg = user_msg + "\n\nKB Snippets:\n" + "\n".join(snippet_texts)
    raw = chat_completion(system, user_msg, max_tokens=700)
    if not raw:
        return {
            'assistant_response': _fallback_response(language),
            'actions': [],
            'errors': ['ai_provider_unavailable'],
        }
    json_text = _extract_json(raw)
    if not json_text:
        return {
            'assistant_response': _fallback_response(language),
            'actions': [],
            'errors': ['invalid_json'],
        }
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        return {
            'assistant_response': _fallback_response(language),
            'actions': [],
            'errors': ['invalid_json'],
        }
    actions, errors = _normalize_actions(payload if isinstance(payload, dict) else {})
    assistant_response = payload.get('assistant_response') if isinstance(payload, dict) else None
    if not assistant_response or not isinstance(assistant_response, str):
        assistant_response = _fallback_response(language)
    return {
        'assistant_response': assistant_response,
        'actions': actions,
        'errors': errors,
    }


def _format_suggest_plans_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when suggest_training_plans succeeded or asks for purpose."""
    for r in results:
        if r.get('action') == 'suggest_training_plans':
            if r.get('status') == 'ask_purpose':
                data = r.get('data') or {}
                return data.get('message_fa') if language == 'fa' else data.get('message_en')
            if r.get('status') != 'ok':
                continue
            data = r.get('data') or {}
            plans = data.get('plans') or []
            if not plans:
                return data.get('message_fa') if language == 'fa' else data.get('message_en')
            lines = []
            if language == 'fa':
                lines.append(f"بر اساس پروفایل شما، {len(plans)} برنامه تمرینی پیشنهاد می‌کنم:\n\n")
            else:
                lines.append(f"Based on your profile, I suggest {len(plans)} training plan(s):\n\n")
            for i, p in enumerate(plans, 1):
                name = p.get('name_fa') or p.get('name_en') or p.get('name', '')
                desc = p.get('description_fa') or p.get('description_en') or p.get('description', '')
                level = p.get('training_level', '')
                weeks = p.get('duration_weeks', 4)
                if language == 'fa':
                    lines.append(f"{i}. **{name}** (سطح: {level}, {weeks} هفته)\n   {desc}\n\n")
                else:
                    lines.append(f"{i}. **{name}** (Level: {level}, {weeks} weeks)\n   {desc}\n\n")
            if language == 'fa':
                lines.append("برای خرید، روی «خرید برنامه» کلیک کنید.")
            else:
                lines.append("To buy, click 'Buy program'.")
            return "".join(lines)
    return None


def _is_buy_or_suggest_program_message(message: str) -> bool:
    """Detect if user wants to buy or get suggestions for a training program."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    buy_suggest = (
        'برنامه بخرم' in m or 'برنامه تمرینی بخرم' in m or 'خرید برنامه' in m or
        'چی پیشنهاد میدی' in m or 'چی پیشنهاد میکنی' in m or 'پیشنهاد میدی' in m or
        'want to buy' in m or 'buy a program' in m or 'suggest' in m or
        'what plan' in m or 'which plan' in m or 'program suggestion' in m
    )
    return buy_suggest


def _message_contains_fitness_goal(message: str) -> bool:
    """Check if message explicitly states a fitness goal (one of the 5).
    If not, we must ask - even if profile has goals (user may have changed intent)."""
    return _extract_goal_from_message(message) is not None


def _extract_goal_from_message(message: str) -> Optional[str]:
    """Extract fitness goal value from message. Returns weight_loss, muscle_gain, strength, endurance, shape_fitting or None."""
    if not message or not isinstance(message, str):
        return None
    m = message.strip().lower()
    # Order matters: check more specific first
    if 'کاهش وزن' in m or 'weight loss' in m or 'lose weight' in m or 'lose fat' in m:
        return 'weight_loss'
    if 'افزایش عضله' in m or 'muscle gain' in m or 'gain muscle' in m:
        return 'muscle_gain'
    if 'قدرت' in m or 'strength' in m:
        return 'muscle_gain'  # map to muscle_gain for purpose
    if 'استقامت' in m or 'endurance' in m:
        return 'endurance'
    if 'انعطاف' in m or 'flexibility' in m:
        return 'shape_fitting'
    if 'تناسب اندام' in m or 'shape fitting' in m or 'general fitness' in m:
        return 'shape_fitting'
    return None


def plan_and_execute(message: str, user: User, language: str) -> Dict[str, Any]:
    plan = plan_actions(message, user, language)
    actions = plan.get('actions', [])
    # If user clearly wants to buy/suggest a program but planner returned wrong action, ensure suggest_training_plans runs
    if _is_buy_or_suggest_program_message(message):
        has_suggest = any(a.get('action') == 'suggest_training_plans' for a in actions)
        wrong_actions = {'create_workout_plan', 'search_exercises'}
        has_wrong = any(a.get('action') in wrong_actions for a in actions)
        if not has_suggest:
            suggest_action = {'action': 'suggest_training_plans', 'params': {'language': language, 'max_results': 4}}
            if has_wrong:
                actions = [a for a in actions if a.get('action') not in wrong_actions] + [suggest_action]
            else:
                actions = actions + [suggest_action]
    # When user states their goal in message, save it to profile before suggesting plans
    extracted_goal = _extract_goal_from_message(message)
    if extracted_goal and any(a.get('action') == 'suggest_training_plans' for a in actions):
        has_update_with_goal = any(
            a.get('action') == 'update_user_profile' and (a.get('params') or {}).get('fields', {}).get('fitness_goals')
            for a in actions
        )
        if not has_update_with_goal:
            update_action = {'action': 'update_user_profile', 'params': {'fields': {'fitness_goals': [extracted_goal]}}}
            actions_list = list(actions)
            for i, a in enumerate(actions_list):
                if a.get('action') == 'suggest_training_plans':
                    actions_list.insert(i, update_action)
                    break
            actions = actions_list
    results = execute_actions(actions, user, language, message)
    assistant_response = plan.get('assistant_response')
    # Override with formatted response when suggest_training_plans succeeded
    formatted = _format_suggest_plans_response(results, language)
    if formatted:
        assistant_response = formatted
    return {
        'assistant_response': assistant_response,
        'actions': plan.get('actions', []),
        'results': results,
        'errors': plan.get('errors', []),
    }


def _fallback_response(language: str) -> str:
    return (
        'متأسفانه الان نمی‌توانم اقدام خودکار انجام دهم. لطفاً دوباره تلاش کنید.'
        if language == 'fa'
        else 'I cannot perform automated actions right now. Please try again.'
    )


def _resolve_relative_date(value: str) -> Optional[str]:
    """Resolve relative date (e.g. tomorrow, in 2 days) to YYYY-MM-DD. Returns None if already YYYY-MM-DD or unparseable."""
    if not value or not isinstance(value, str):
        return None
    s = value.strip().lower()
    today = datetime.utcnow().date()
    # Already ISO date
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    # tomorrow, tomorrow evening, etc.
    if s in ('tomorrow', 'فردا'):
        return (today + timedelta(days=1)).isoformat()
    # today
    if s in ('today', 'امروز'):
        return today.isoformat()
    # in N days
    m = re.match(r'^in\s+(\d+)\s+days?$', s)
    if m:
        n = int(m.group(1))
        return (today + timedelta(days=n)).isoformat()
    m = re.match(r'^(\d+)\s+days?\s+from\s+now$', s)
    if m:
        n = int(m.group(1))
        return (today + timedelta(days=n)).isoformat()
    # next week
    if s in ('next week', 'هفته بعد'):
        return (today + timedelta(days=7)).isoformat()
    # day after tomorrow
    if s in ('day after tomorrow', 'پس‌فردا'):
        return (today + timedelta(days=2)).isoformat()
    return None


def _resolve_relative_time(value: str) -> Optional[str]:
    """Resolve relative time (e.g. morning, evening) to HH:MM. Returns None if already HH:MM or unparseable."""
    if not value or not isinstance(value, str):
        return None
    s = value.strip().lower()
    # Already time-like HH:MM or H:MM
    if re.match(r'^\d{1,2}:\d{2}(?:\s*[ap]m)?$', s):
        s = s.replace(' ', '')
        if 'pm' in s:
            h = int(s.split(':')[0])
            if h < 12:
                return f"{h + 12:02d}:{s.split(':')[1][:2]}"
            return f"{h:02d}:{s.split(':')[1][:2]}"
        if 'am' in s:
            h = int(s.split(':')[0])
            if h == 12:
                return "00:00"
            return f"{h:02d}:{s.split(':')[1][:2]}"
        return s[:5] if len(s) >= 5 else s
    # morning -> 09:00, afternoon -> 14:00, evening -> 18:00, night -> 20:00
    if s in ('morning', 'صبح', 'am'):
        return '09:00'
    if s in ('afternoon', 'ظهر', 'noon', 'midday'):
        return '14:00'
    if s in ('evening', 'عصر'):
        return '18:00'
    if s in ('night', 'شب'):
        return '20:00'
    return None


def execute_actions(actions: List[Dict[str, Any]], user: User, language: str, message: str = '') -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for action_item in actions:
        action = action_item.get('action')
        params = action_item.get('params') or {}
        try:
            if action == 'search_exercises':
                results.append(_exec_search_exercises(params, user, language))
            elif action == 'create_workout_plan':
                results.append(_exec_create_workout_plan(params, user, language))
            elif action == 'suggest_training_plans':
                results.append(_exec_suggest_training_plans(params, user, language, message))
            elif action == 'update_user_profile':
                results.append(_exec_update_user_profile(params, user, language))
            elif action == 'progress_check':
                results.append(_exec_progress_check(params, user, language))
            elif action == 'trainer_message':
                results.append(_exec_trainer_message(params, user, language))
            elif action == 'site_settings':
                results.append(_exec_site_settings(params, user, language))
            elif action in ('schedule_meeting', 'schedule_appointment'):
                results.append(_exec_schedule_meeting(params, user, language))
            else:
                results.append({'action': action, 'status': 'error', 'error': 'unsupported_action'})
        except Exception as e:
            results.append({'action': action, 'status': 'error', 'error': str(e)})
    return results


def _exec_search_exercises(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    query_text = (params.get('query') or '').strip()
    target_muscle = (params.get('target_muscle') or '').strip()
    level = (params.get('level') or '').strip().lower()
    intensity = (params.get('intensity') or '').strip().lower()
    max_results = params.get('max_results') or 10
    try:
        max_results = int(max_results)
    except (ValueError, TypeError):
        max_results = 10
    if max_results < 1:
        max_results = 1
    if max_results > 50:
        max_results = 50

    db = _db()
    user_profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
    q = db.session.query(Exercise)
    if user_profile and not user_profile.gym_access:
        q = q.filter(Exercise.category == 'functional_home')
    if level:
        q = q.filter(Exercise.level == level)
    if intensity:
        q = q.filter(Exercise.intensity == intensity)

    if query_text:
        q = q.filter(
            (Exercise.name_fa.contains(query_text)) |
            (Exercise.name_en.contains(query_text)) |
            (Exercise.target_muscle_fa.contains(query_text)) |
            (Exercise.target_muscle_en.contains(query_text))
        )
    if target_muscle:
        q = q.filter(
            (Exercise.target_muscle_fa.contains(target_muscle)) |
            (Exercise.target_muscle_en.contains(target_muscle))
        )

    injuries = []
    if user_profile:
        injuries = user_profile.get_injuries()
    for injury in injuries:
        q = q.filter(~Exercise.injury_contraindications.contains(f'"{injury}"'))

    items = q.limit(max_results).all()
    return {
        'action': 'search_exercises',
        'status': 'ok',
        'data': [ex.to_dict(language) for ex in items],
    }


def _exec_create_workout_plan(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    month = params.get('month', 1)
    try:
        month = int(month)
    except (ValueError, TypeError):
        month = 1
    if month < 1 or month > 6:
        month = 1
    target_muscle = (params.get('target_muscle') or '').strip()
    message = f"workout plan for {target_muscle}" if target_muscle else "workout plan"
    if language == 'fa':
        message = f"برنامه تمرینی برای {target_muscle}" if target_muscle else "برنامه تمرینی"

    db = _db()
    coach = PersianFitnessCoachAI(user.id)
    user_injuries = []
    if coach.user_profile:
        user_injuries = list(coach.user_profile.get_injuries() or [])
        medical = coach.user_profile.get_medical_conditions() if hasattr(coach.user_profile, 'get_medical_conditions') else []
        if medical:
            user_injuries = list(set(user_injuries + [m for m in medical if m and str(m).strip()]))
    q = db.session.query(Exercise)
    if coach.user_profile and not coach.user_profile.gym_access:
        q = q.filter(Exercise.category == 'functional_home')
    exercise_pool = q.limit(50).all()
    plan = coach._handle_workout_plan_request(message, month, user_injuries, exercise_pool, language)
    return {
        'action': 'create_workout_plan',
        'status': 'ok',
        'data': plan,
    }


def _exec_suggest_training_plans(params: Dict[str, Any], user: User, language: str, message: str = '') -> Dict[str, Any]:
    """Suggest up to 4 training plans from general programs, filtered by user profile.
    ALWAYS ask for fitness goal when message doesn't explicitly state it - even if profile has goals."""
    max_results = params.get('max_results') or 4
    try:
        max_results = min(int(max_results), 4)
    except (ValueError, TypeError):
        max_results = 4

    db = _db()
    profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
    goals = profile.get_fitness_goals() if profile and hasattr(profile, 'get_fitness_goals') else []
    message_has_goal = _message_contains_fitness_goal(message)
    profile_has_goal = bool(goals) and (not isinstance(goals, list) or len(goals) > 0)
    # Ask for goal when: profile has no goal OR message doesn't explicitly state goal
    must_ask_purpose = not profile_has_goal or not message_has_goal
    if must_ask_purpose:
        return {
            'action': 'suggest_training_plans',
            'status': 'ask_purpose',
            'data': {
                'message_fa': 'برای پیشنهاد برنامه مناسب، لطفاً هدف خود را بگویید: کاهش وزن، افزایش عضله، قدرت، استقامت، یا انعطاف‌پذیری.',
                'message_en': 'To suggest a suitable plan, please tell me your goal: weight loss, muscle gain, strength, endurance, or flexibility.',
            },
        }
    user_level = (profile.training_level or 'beginner').strip().lower() if profile else 'beginner'
    gym_access = profile.gym_access if profile and profile.gym_access is not None else True

    q = db.session.query(TrainingProgram).filter(TrainingProgram.user_id.is_(None)).order_by(TrainingProgram.id)
    programs = q.limit(20).all()
    # If no gym access, prefer functional programs first
    if not gym_access:
        functional = [p for p in programs if p.category and 'functional' in (p.category or '').lower()]
        others = [p for p in programs if p not in functional]
        filtered = functional + others
    else:
        filtered = programs

    # Get prices from SiteSettings.training_plans_products_json - match by id only
    price_by_id: Dict[int, float] = {}
    try:
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        raw = getattr(row, 'training_plans_products_json', None) or ''
        if raw:
            data = json.loads(raw)
            for bp in (data.get('basePrograms') or []):
                pid = bp.get('id')
                if pid is not None:
                    try:
                        price_by_id[int(pid)] = float(bp.get('price', 0))
                    except (ValueError, TypeError):
                        pass
    except Exception:
        pass

    plans_data = []
    for p in filtered[:max_results]:
        d = p.to_dict(language)
        price = price_by_id.get(p.id, 0)
        if price <= 0:
            price = 99.0  # Default so user can always buy the AI-suggested program
        d['price'] = price
        plans_data.append(d)
    if not plans_data:
        return {
            'action': 'suggest_training_plans',
            'status': 'ok',
            'data': {
                'plans': [],
                'message_fa': 'در حال حاضر برنامه‌ای موجود نیست. لطفاً با پشتیبانی تماس بگیرید.',
                'message_en': 'No programs available at the moment. Please contact support.',
            },
        }

    return {
        'action': 'suggest_training_plans',
        'status': 'ok',
        'data': {
            'plans': plans_data,
            'count': len(plans_data),
        },
    }


def _exec_update_user_profile(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    fields = params.get('fields') or {}
    if not isinstance(fields, dict):
        return {'action': 'update_user_profile', 'status': 'error', 'error': 'fields_must_be_object'}

    target_user_id = params.get('user_id')
    if target_user_id is not None:
        try:
            target_user_id = int(target_user_id)
        except (ValueError, TypeError):
            return {'action': 'update_user_profile', 'status': 'error', 'error': 'invalid_user_id'}
        if user.role != 'admin' and target_user_id != user.id:
            return {'action': 'update_user_profile', 'status': 'error', 'error': 'forbidden'}
    else:
        target_user_id = user.id

    db = _db()
    profile = db.session.query(UserProfile).filter_by(user_id=target_user_id).first()
    if not profile:
        profile = UserProfile(user_id=target_user_id)
        db.session.add(profile)

    updated = {}
    for key, value in fields.items():
        if key not in PROFILE_FIELDS_ALLOWED:
            continue
        if key in ('fitness_goals', 'injuries', 'equipment_access', 'medical_conditions', 'home_equipment'):
            if isinstance(value, list):
                setattr(profile, key, json.dumps(value, ensure_ascii=False))
                updated[key] = value
        else:
            setattr(profile, key, value)
            updated[key] = value
    db.session.commit()
    return {
        'action': 'update_user_profile',
        'status': 'ok',
        'data': {'user_id': target_user_id, 'updated': updated},
    }


def _exec_progress_check(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    mode = (params.get('mode') or '').strip().lower()
    db = _db()
    if mode == 'request':
        if user.role != 'member':
            return {'action': 'progress_check', 'status': 'error', 'error': 'only_member_can_request'}
        req = ProgressCheckRequest(member_id=user.id, status='pending', requested_at=datetime.utcnow())
        db.session.add(req)
        db.session.commit()
        return {
            'action': 'progress_check',
            'status': 'ok',
            'data': {'request_id': req.id, 'status': req.status},
        }
    if mode == 'respond':
        if user.role not in ('admin', 'assistant'):
            return {'action': 'progress_check', 'status': 'error', 'error': 'forbidden'}
        request_id = params.get('request_id')
        status = (params.get('status') or '').strip().lower()
        if status not in ('accepted', 'denied'):
            return {'action': 'progress_check', 'status': 'error', 'error': 'invalid_status'}
        try:
            request_id = int(request_id)
        except (ValueError, TypeError):
            return {'action': 'progress_check', 'status': 'error', 'error': 'invalid_request_id'}
        req = db.session.query(ProgressCheckRequest).filter_by(id=request_id).first()
        if not req:
            return {'action': 'progress_check', 'status': 'error', 'error': 'not_found'}
        req.status = status
        req.responded_at = datetime.utcnow()
        req.responded_by = user.id
        db.session.commit()
        return {
            'action': 'progress_check',
            'status': 'ok',
            'data': {'request_id': req.id, 'status': req.status},
        }
    return {'action': 'progress_check', 'status': 'error', 'error': 'invalid_mode'}


def _exec_trainer_message(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    body = (params.get('body') or '').strip()
    if not body:
        return {'action': 'trainer_message', 'status': 'error', 'error': 'body_required'}

    db = _db()
    recipient_id = params.get('recipient_id')
    if user.role == 'member':
        recipient_id = getattr(user, 'assigned_to', None)
        if not recipient_id:
            return {'action': 'trainer_message', 'status': 'error', 'error': 'no_trainer_assigned'}
    else:
        if recipient_id is None:
            return {'action': 'trainer_message', 'status': 'error', 'error': 'recipient_id_required'}
        try:
            recipient_id = int(recipient_id)
        except (ValueError, TypeError):
            return {'action': 'trainer_message', 'status': 'error', 'error': 'invalid_recipient_id'}
        recipient = db.session.get(User, recipient_id)
        if not recipient or recipient.role != 'member':
            return {'action': 'trainer_message', 'status': 'error', 'error': 'invalid_recipient'}
        if user.role == 'assistant' and getattr(recipient, 'assigned_to', None) != user.id:
            return {'action': 'trainer_message', 'status': 'error', 'error': 'forbidden'}

    msg = TrainerMessage(sender_id=user.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    return {
        'action': 'trainer_message',
        'status': 'ok',
        'data': {'id': msg.id, 'recipient_id': recipient_id},
    }


def _exec_site_settings(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    if user.role != 'admin':
        return {'action': 'site_settings', 'status': 'error', 'error': 'forbidden'}
    fields = params.get('fields') or {}
    if not isinstance(fields, dict):
        return {'action': 'site_settings', 'status': 'error', 'error': 'fields_must_be_object'}
    db = _db()
    row = db.session.query(SiteSettings).first()
    if not row:
        row = SiteSettings()
        db.session.add(row)
    updated = {}
    for key, value in fields.items():
        if key not in SITE_SETTINGS_FIELDS_ALLOWED:
            continue
        setattr(row, key, value)
        updated[key] = value
    db.session.commit()
    return {
        'action': 'site_settings',
        'status': 'ok',
        'data': {'updated': updated},
    }


def _exec_schedule_meeting(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Resolve relative date/time to exact values and return the scheduled slot. Does not persist (no Meeting model)."""
    raw_date = (params.get('appointment_date') or '').strip() or None
    raw_time = (params.get('appointment_time') or '').strip() or None
    duration = params.get('duration', 60)
    notes = (params.get('notes') or '').strip() or ''
    try:
        duration = int(duration)
    except (ValueError, TypeError):
        duration = 60
    if duration < 15:
        duration = 15
    if duration > 240:
        duration = 240

    # Resolve date: relative -> YYYY-MM-DD
    resolved_date = None
    if raw_date:
        resolved_date = _resolve_relative_date(raw_date)
        if not resolved_date:
            resolved_date = raw_date if re.match(r'^\d{4}-\d{2}-\d{2}$', raw_date.strip()) else None
    if not resolved_date:
        resolved_date = (datetime.utcnow().date() + timedelta(days=1)).isoformat()

    # Resolve time: relative -> HH:MM
    resolved_time = None
    if raw_time:
        resolved_time = _resolve_relative_time(raw_time)
        if not resolved_time:
            resolved_time = raw_time if re.match(r'^\d{1,2}:\d{2}', raw_time.strip()) else None
    if not resolved_time:
        resolved_time = '18:00'

    return {
        'action': 'schedule_meeting',
        'status': 'ok',
        'data': {
            'resolved_date': resolved_date,
            'resolved_time': resolved_time,
            'duration_minutes': duration,
            'notes': notes,
            'message_fa': f"جلسه برای {resolved_date} ساعت {resolved_time} به مدت {duration} دقیقه ثبت شد.",
            'message_en': f"Meeting scheduled for {resolved_date} at {resolved_time} for {duration} minutes.",
        },
    }
