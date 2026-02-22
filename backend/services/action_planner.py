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
from models import Exercise, UserProfile, SiteSettings, ProgressCheckRequest, TrainingProgram, MemberTrainingActionCompletion
from models_workout_log import ProgressEntry


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
    'get_dashboard_progress',
    'add_progress_entry',
    'get_todays_training',
    'get_dashboard_tab_info',
    'get_trainers_info',
    'get_member_progress',
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
    'get_dashboard_progress': {
        'required': [],
        'optional': ['language', 'fields'],
    },
    'add_progress_entry': {
        'required': [],
        'optional': ['weight_kg', 'chest_cm', 'waist_cm', 'hips_cm', 'arm_left_cm', 'arm_right_cm', 'thigh_left_cm', 'thigh_right_cm', 'form_level', 'body_fat_percentage', 'muscle_mass_kg'],
    },
    'get_todays_training': {
        'required': [],
        'optional': ['language'],
    },
    'get_dashboard_tab_info': {
        'required': ['tab'],
        'optional': ['language'],
    },
    'get_trainers_info': {
        'required': [],
        'optional': ['language'],
    },
    'get_member_progress': {
        'required': [],
        'optional': ['member_id', 'member_username', 'language'],
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
        "progress_check, trainer_message, site_settings, schedule_meeting, schedule_appointment, "
        "get_dashboard_progress, add_progress_entry, get_todays_training, get_dashboard_tab_info, get_trainers_info, get_member_progress. "
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
        "- get_dashboard_progress: params { language?, fields? } - use when user asks about BMI, weight, progress, dashboard, روند تغییرات, پیشرفت. Returns profile weight/height, BMI, progress entries. ALWAYS ask if they want to add new weight to Progress Trend.\n"
        "- add_progress_entry: params { weight_kg?, chest_cm?, waist_cm?, hips_cm?, arm_left_cm?, arm_right_cm?, thigh_left_cm?, thigh_right_cm? } - use when user wants to add/record weight or measurements to Progress Trend. Extract numbers from message (e.g. 'add 76 kg' -> weight_kg: 76).\n"
        "- get_todays_training: params { language? } - use when user asks 'what is my training today', 'جلسه امروز', 'برنامه امروز', 'today workout', 'my workout today'. Returns next session to do.\n"
        "- get_dashboard_tab_info: params { tab: 'psychology-test'|'online-lab', language? } - use when user asks about Psychology Test (تست روانشناسی), Online Laboratory (آزمایشگاه آنلاین), or what info those tabs need. tab='psychology-test' or 'online-lab'.\n"
        "- get_trainers_info: params { language? } - use when admin or assistant asks about trainers, assistants, مربی‌ها, دستیاران, list of trainers, my assigned members. Admin sees all assistants; assistant sees only their own info (their trainees count). Admin/assistant only.\n"
        "- get_member_progress: params { member_id?, member_username?, language? } - use when admin or assistant asks about a specific member's progress, weight, BMI, situation, وضعیت عضو, پیشرفت عضو. Assistant can only query their assigned members (assigned_to=assistant). Admin can query any member. Provide member_id or member_username to identify the member.\n"
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


def _format_dashboard_progress_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when get_dashboard_progress succeeded. Include data and ask if they want to add new weight."""
    for r in results:
        if r.get('action') != 'get_dashboard_progress' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        weight = data.get('weight_kg')
        height = data.get('height_cm')
        bmi = data.get('bmi')
        entries = data.get('progress_entries') or []
        fa = language == 'fa'
        lines = []
        if bmi is not None:
            if fa:
                lines.append(f"BMI فعلی شما: **{bmi}** است.")
                if weight is not None:
                    lines.append(f"وزن: {weight} کیلوگرم.")
                if height is not None:
                    lines.append(f"قد: {height} سانتی‌متر.")
            else:
                lines.append(f"Your current BMI is **{bmi}**.")
                if weight is not None:
                    lines.append(f"Weight: {weight} kg.")
                if height is not None:
                    lines.append(f"Height: {height} cm.")
        elif weight is not None:
            if fa:
                lines.append(f"وزن فعلی شما: **{weight}** کیلوگرم است.")
            else:
                lines.append(f"Your current weight is **{weight}** kg.")
        else:
            if fa:
                lines.append("هنوز وزن یا قد در پروفایل ثبت نشده. لطفاً در بخش پروفایل آن‌ها را وارد کنید.")
            else:
                lines.append("Weight and height are not set in your profile yet. Please add them in the Profile section.")
        if fa:
            lines.append("\nآیا می‌خواهید وزن جدید را به روند تغییرات اضافه کنید؟")
        else:
            lines.append("\nWould you like to add new weight to your Progress Trend?")
        return "\n".join(lines)
    return None


def _format_add_progress_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when add_progress_entry succeeded."""
    for r in results:
        if r.get('action') != 'add_progress_entry' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        return data.get('message_fa') if language == 'fa' else data.get('message_en')
    return None


def _format_todays_training_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when get_todays_training succeeded."""
    for r in results:
        if r.get('action') != 'get_todays_training' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        if data.get('all_done'):
            return data.get('message_fa') if language == 'fa' else data.get('message_en')
        if not data.get('has_program'):
            return data.get('message_fa') if language == 'fa' else data.get('message_en')
        fa = language == 'fa'
        lines = []
        if fa:
            lines.append(f"**{data.get('session_name', '')}** از برنامه {data.get('program_name', '')}:\n\n")
        else:
            lines.append(f"**{data.get('session_name', '')}** from {data.get('program_name', '')}:\n\n")
        for i, ex in enumerate((data.get('exercises') or []), 1):
            name = ex.get('name', '')
            sets = ex.get('sets', '')
            reps = ex.get('reps', '')
            if fa:
                lines.append(f"{i}. {name} – {sets} ست × {reps} تکرار\n")
            else:
                lines.append(f"{i}. {name} – {sets} sets × {reps} reps\n")
        if fa:
            lines.append("\nبرای شروع به داشبورد > برنامه تمرینی بروید.")
        else:
            lines.append("\nGo to Dashboard > Training Program to start.")
        return "".join(lines)
    return None


def _format_dashboard_tab_info_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when get_dashboard_tab_info succeeded."""
    for r in results:
        if r.get('action') != 'get_dashboard_tab_info' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        return data.get('description_fa') if language == 'fa' else data.get('description_en')
    return None


def _format_member_progress_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when get_member_progress succeeded."""
    for r in results:
        if r.get('action') != 'get_member_progress' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        member_name = data.get('member_username') or data.get('member_name') or 'Member'
        weight = data.get('weight_kg')
        height = data.get('height_cm')
        bmi = data.get('bmi')
        entries = data.get('progress_entries') or []
        fa = language == 'fa'
        lines = []
        if fa:
            lines.append(f"**وضعیت عضو {member_name}:**\n\n")
        else:
            lines.append(f"**{member_name}'s progress:**\n\n")
        if bmi is not None:
            if fa:
                lines.append(f"BMI: **{bmi}**")
                if weight is not None:
                    lines.append(f" | وزن: {weight} کیلوگرم")
                if height is not None:
                    lines.append(f" | قد: {height} سانتی‌متر")
            else:
                lines.append(f"BMI: **{bmi}**")
                if weight is not None:
                    lines.append(f" | Weight: {weight} kg")
                if height is not None:
                    lines.append(f" | Height: {height} cm")
            lines.append("\n")
        elif weight is not None:
            if fa:
                lines.append(f"وزن فعلی: **{weight}** کیلوگرم\n")
            else:
                lines.append(f"Current weight: **{weight}** kg\n")
        else:
            if fa:
                lines.append("هنوز وزن یا قد در پروفایل ثبت نشده.\n")
            else:
                lines.append("Weight and height are not set in profile yet.\n")
        if entries:
            if fa:
                lines.append(f"آخرین {len(entries)} رکورد روند تغییرات:\n")
            else:
                lines.append(f"Last {len(entries)} progress entries:\n")
            for e in entries[:5]:
                rec = e.get('recorded_at') or ''
                if rec:
                    try:
                        dt = datetime.fromisoformat(rec.replace('Z', '+00:00'))
                        rec = dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
                w = e.get('weight_kg')
                if w is not None:
                    if fa:
                        lines.append(f"  • {rec}: {w} کیلوگرم\n")
                    else:
                        lines.append(f"  • {rec}: {w} kg\n")
        return "".join(lines)
    return None


def _format_trainers_info_response(results: List[Dict[str, Any]], language: str) -> Optional[str]:
    """Build user-facing response when get_trainers_info succeeded."""
    for r in results:
        if r.get('action') != 'get_trainers_info' or r.get('status') != 'ok':
            continue
        data = r.get('data') or {}
        trainers = data.get('trainers') or []
        if not trainers:
            return 'لیست مربیان خالی است.' if language == 'fa' else 'No trainers found.'
        fa = language == 'fa'
        lines = []
        if fa:
            lines.append(f"**{len(trainers)} مربی/دستیار:**\n\n")
        else:
            lines.append(f"**{len(trainers)} trainer(s):**\n\n")
        for i, t in enumerate(trainers, 1):
            name = t.get('username', '') or t.get('email', '')
            count = t.get('assigned_members_count', 0)
            if fa:
                lines.append(f"{i}. {name} – {count} عضو تخصیص یافته\n")
            else:
                lines.append(f"{i}. {name} – {count} assigned member(s)\n")
        return "".join(lines)
    return None


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


def _is_todays_training_message(message: str) -> bool:
    """Detect if user asks about today's training/workout."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    return (
        'training today' in m or 'workout today' in m or 'today workout' in m or 'today training' in m or
        'my training' in m or 'my workout' in m or 'what is my training' in m or 'what is my workout' in m or
        'جلسه امروز' in m or 'برنامه امروز' in m or 'تمرین امروز' in m or 'ورزش امروز' in m
    )


def _is_member_progress_message(message: str) -> bool:
    """Detect if admin/assistant asks about a member's progress/situation."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    return (
        'member' in m and ('progress' in m or 'weight' in m or 'bmi' in m or 'situation' in m or 'وضعیت' in m or 'پیشرفت' in m) or
        'وضعیت عضو' in m or 'پیشرفت عضو' in m or 'چک کن' in m and 'عضو' in m or
        'check member' in m or 'member progress' in m or 'member situation' in m
    )


def _is_trainers_info_message(message: str) -> bool:
    """Detect if admin/assistant asks about trainers, assistants."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    return (
        'trainer' in m or 'assistant' in m or 'مربی' in m or 'دستیار' in m or
        'list of trainers' in m or 'assigned members' in m or 'اعضای تخصیص' in m
    )


def _is_dashboard_tab_message(message: str) -> bool:
    """Detect if user asks about Psychology Test or Online Laboratory."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    return (
        'psychology' in m or 'تست روانشناسی' in m or 'روانشناسی' in m or
        'online lab' in m or 'online laboratory' in m or 'آزمایشگاه آنلاین' in m or 'آزمایشگاه' in m
    )


def _is_dashboard_progress_message(message: str) -> bool:
    """Detect if user asks about BMI, weight, progress, dashboard."""
    if not message or not isinstance(message, str):
        return False
    m = message.strip().lower()
    return (
        'bmi' in m or 'وزن' in m or 'قد' in m or 'weight' in m or 'height' in m or
        'پیشرفت' in m or 'progress' in m or 'روند تغییرات' in m or 'progress trend' in m or
        'داشبورد' in m or 'dashboard' in m or 'اندازه' in m or 'measurement' in m
    )


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
    # If user asks about dashboard/progress but planner didn't return get_dashboard_progress, inject it
    if _is_dashboard_progress_message(message):
        has_progress = any(a.get('action') == 'get_dashboard_progress' for a in actions)
        if not has_progress:
            actions = actions + [{'action': 'get_dashboard_progress', 'params': {'language': language}}]
    # If user asks about today's training but planner didn't return get_todays_training, inject it
    if _is_todays_training_message(message):
        has_training = any(a.get('action') == 'get_todays_training' for a in actions)
        if not has_training:
            actions = actions + [{'action': 'get_todays_training', 'params': {'language': language}}]
    # If admin/assistant asks about trainers but planner didn't return get_trainers_info, inject it
    if getattr(user, 'role', None) in ('admin', 'assistant') and _is_trainers_info_message(message):
        has_trainers = any(a.get('action') == 'get_trainers_info' for a in actions)
        if not has_trainers:
            actions = actions + [{'action': 'get_trainers_info', 'params': {'language': language}}]
    # If user asks about Psychology Test or Online Lab but planner didn't return get_dashboard_tab_info, inject it
    if _is_dashboard_tab_message(message):
        has_tab_info = any(a.get('action') == 'get_dashboard_tab_info' for a in actions)
        if not has_tab_info:
            m = message.lower()
            tab = 'online-lab' if ('lab' in m or 'آزمایشگاه' in m or 'laboratory' in m) else 'psychology-test'
            actions = actions + [{'action': 'get_dashboard_tab_info', 'params': {'tab': tab, 'language': language}}]
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
    # Override when get_dashboard_progress or add_progress_entry succeeded
    if not formatted:
        formatted = _format_dashboard_progress_response(results, language)
        if formatted:
            assistant_response = formatted
    if not formatted:
        formatted = _format_add_progress_response(results, language)
        if formatted:
            assistant_response = formatted
    if not formatted:
        formatted = _format_todays_training_response(results, language)
        if formatted:
            assistant_response = formatted
    if not formatted:
        formatted = _format_dashboard_tab_info_response(results, language)
        if formatted:
            assistant_response = formatted
    if not formatted:
        formatted = _format_trainers_info_response(results, language)
        if formatted:
            assistant_response = formatted
    if not formatted:
        formatted = _format_member_progress_response(results, language)
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
            elif action == 'get_dashboard_progress':
                results.append(_exec_get_dashboard_progress(params, user, language))
            elif action == 'add_progress_entry':
                results.append(_exec_add_progress_entry(params, user, language))
            elif action == 'get_todays_training':
                results.append(_exec_get_todays_training(params, user, language))
            elif action == 'get_dashboard_tab_info':
                results.append(_exec_get_dashboard_tab_info(params, user, language))
            elif action == 'get_trainers_info':
                results.append(_exec_get_trainers_info(params, user, language))
            elif action == 'get_member_progress':
                results.append(_exec_get_member_progress(params, user, language))
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


def _exec_get_dashboard_progress(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Fetch user's profile (weight, height), BMI, and progress entries for dashboard/progress queries."""
    db = _db()
    profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
    weight = profile.weight if profile and profile.weight is not None else None
    height = profile.height if profile and profile.height is not None else None
    bmi = None
    if weight and height and height > 0:
        height_m = height / 100.0
        bmi = round(weight / (height_m * height_m), 1)
    limit = 10
    entries = db.session.query(ProgressEntry).filter_by(user_id=user.id)\
        .order_by(ProgressEntry.recorded_at.desc()).limit(limit).all()
    progress_entries = [{
        'weight_kg': e.weight_kg,
        'chest_cm': e.chest_cm,
        'waist_cm': e.waist_cm,
        'hips_cm': e.hips_cm,
        'recorded_at': e.recorded_at.isoformat() if e.recorded_at else None,
    } for e in entries]
    return {
        'action': 'get_dashboard_progress',
        'status': 'ok',
        'data': {
            'weight_kg': weight,
            'height_cm': height,
            'bmi': bmi,
            'progress_entries': progress_entries,
            'language': params.get('language') or language,
        },
    }


def _exec_add_progress_entry(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Add a new progress entry (weight, measurements) to Progress Trend."""
    db = _db()

    def _float_or_none(v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    weight_kg = _float_or_none(params.get('weight_kg'))
    chest_cm = _float_or_none(params.get('chest_cm'))
    waist_cm = _float_or_none(params.get('waist_cm'))
    hips_cm = _float_or_none(params.get('hips_cm'))
    arm_left_cm = _float_or_none(params.get('arm_left_cm'))
    arm_right_cm = _float_or_none(params.get('arm_right_cm'))
    thigh_left_cm = _float_or_none(params.get('thigh_left_cm'))
    thigh_right_cm = _float_or_none(params.get('thigh_right_cm'))
    form_level = params.get('form_level')
    form_level = int(form_level) if form_level is not None else None
    body_fat_percentage = _float_or_none(params.get('body_fat_percentage'))
    muscle_mass_kg = _float_or_none(params.get('muscle_mass_kg'))

    if weight_kg is None and chest_cm is None and waist_cm is None and hips_cm is None:
        return {
            'action': 'add_progress_entry',
            'status': 'error',
            'error': 'at_least_one_field_required',
            'message_fa': 'لطفاً حداقل وزن یا یکی از اندازه‌گیری‌ها را وارد کنید.',
            'message_en': 'Please provide at least weight or one measurement.',
        }
    if weight_kg is not None:
        profile = db.session.query(UserProfile).filter_by(user_id=user.id).first()
        if profile:
            profile.weight = weight_kg
            db.session.flush()
    entry = ProgressEntry(
        user_id=user.id,
        weight_kg=weight_kg,
        chest_cm=chest_cm,
        waist_cm=waist_cm,
        hips_cm=hips_cm,
        arm_left_cm=arm_left_cm,
        arm_right_cm=arm_right_cm,
        thigh_left_cm=thigh_left_cm,
        thigh_right_cm=thigh_right_cm,
        form_level=int(form_level) if form_level is not None else None,
        body_fat_percentage=float(body_fat_percentage) if body_fat_percentage is not None else None,
        muscle_mass_kg=float(muscle_mass_kg) if muscle_mass_kg is not None else None,
    )
    db.session.add(entry)
    db.session.commit()
    return {
        'action': 'add_progress_entry',
        'status': 'ok',
        'data': {
            'progress_entry_id': entry.id,
            'weight_kg': weight_kg,
            'message_fa': f'وزن {weight_kg} کیلوگرم به روند تغییرات اضافه شد.' if weight_kg else 'اطلاعات به روند تغییرات اضافه شد.',
            'message_en': f'Weight {weight_kg} kg added to Progress Trend.' if weight_kg else 'Data added to Progress Trend.',
        },
    }


def _exec_get_todays_training(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Fetch user's next training session (first incomplete session) for 'today's training' queries."""
    db = _db()
    programs = db.session.query(TrainingProgram).filter_by(user_id=user.id).all()
    if not programs:
        return {
            'action': 'get_todays_training',
            'status': 'ok',
            'data': {
                'has_program': False,
                'message_fa': 'شما هنوز برنامه تمرینی ندارید. برای خرید برنامه به بخش برنامه تمرینی مراجعه کنید.',
                'message_en': "You don't have a training program yet. Go to the Training Program section to purchase one.",
            },
        }
    fa = language == 'fa'
    for program in programs:
        sessions = program.get_sessions() or []
        for idx, session in enumerate(sessions):
            exercises = session.get('exercises') or []
            if not exercises:
                continue
            completed = db.session.query(MemberTrainingActionCompletion).filter_by(
                user_id=user.id,
                training_program_id=program.id,
                session_index=idx,
            ).count()
            if completed < len(exercises):
                session_name = (session.get('name_fa') if fa else session.get('name_en')) or session.get('name_fa') or session.get('name_en') or ''
                program_name = (program.name_fa if fa else program.name_en) or program.name_fa or program.name_en
                ex_list = []
                for ex in exercises[:12]:
                    name = (ex.get('name_fa') if fa else ex.get('name_en')) or ex.get('name_fa') or ex.get('name_en') or ''
                    sets = ex.get('sets', '')
                    reps = ex.get('reps', '')
                    ex_list.append({'name': name, 'sets': sets, 'reps': reps})
                return {
                    'action': 'get_todays_training',
                    'status': 'ok',
                    'data': {
                        'has_program': True,
                        'program_name': program_name,
                        'session_name': session_name,
                        'session_index': idx,
                        'exercises': ex_list,
                        'language': language,
                    },
                }
    return {
        'action': 'get_todays_training',
        'status': 'ok',
        'data': {
            'has_program': True,
            'all_done': True,
            'message_fa': 'همه جلسات شما انجام شده! استراحت کنید یا برنامه جدیدی شروع کنید.',
            'message_en': "All your sessions are done! Rest or start a new program.",
        },
    }


def _exec_get_trainers_info(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Return list of trainers (assistants). Admin sees all; assistant sees only their own trainees info."""
    if getattr(user, 'role', None) not in ('admin', 'assistant'):
        return {
            'action': 'get_trainers_info',
            'status': 'error',
            'error': 'forbidden',
            'message_fa': 'فقط ادمین و دستیار می‌توانند اطلاعات مربیان را ببینند.',
            'message_en': 'Only admin and assistant can view trainers info.',
        }
    db = _db()
    if user.role == 'assistant':
        # Assistant sees only their own info (their trainees count)
        count = db.session.query(User).filter_by(assigned_to=user.id).count()
        trainers_data = [{
            'id': user.id,
            'username': user.username or '',
            'email': user.email or '',
            'assigned_members_count': count,
        }]
    else:
        # Admin sees all assistants
        assistants = db.session.query(User).filter_by(role='assistant').all()
        trainers_data = []
        for a in assistants:
            count = db.session.query(User).filter_by(assigned_to=a.id).count()
            trainers_data.append({
                'id': a.id,
                'username': a.username or '',
                'email': a.email or '',
                'assigned_members_count': count,
            })
    return {
        'action': 'get_trainers_info',
        'status': 'ok',
        'data': {
            'trainers': trainers_data,
            'language': params.get('language') or language,
        },
    }


def _exec_get_member_progress(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Return a specific member's progress (weight, BMI, progress entries). Assistant: only their assigned members. Admin: any member."""
    if getattr(user, 'role', None) not in ('admin', 'assistant'):
        return {
            'action': 'get_member_progress',
            'status': 'error',
            'error': 'forbidden',
            'message_fa': 'فقط ادمین و دستیار می‌توانند پیشرفت اعضا را ببینند.',
            'message_en': 'Only admin and assistant can view member progress.',
        }
    db = _db()
    member_id = params.get('member_id')
    member_username = (params.get('member_username') or '').strip()
    member = None
    if member_id is not None:
        try:
            member = db.session.get(User, int(member_id))
        except (ValueError, TypeError):
            pass
    if not member and member_username:
        member = db.session.query(User).filter_by(username=member_username, role='member').first()
    if not member or member.role != 'member':
        return {
            'action': 'get_member_progress',
            'status': 'error',
            'error': 'member_not_found',
            'message_fa': 'عضو یافت نشد. لطفاً شناسه یا نام کاربری عضو را مشخص کنید.',
            'message_en': 'Member not found. Please specify member_id or member_username.',
        }
    if user.role == 'assistant' and getattr(member, 'assigned_to', None) != user.id:
        return {
            'action': 'get_member_progress',
            'status': 'error',
            'error': 'forbidden',
            'message_fa': 'شما فقط می‌توانید پیشرفت اعضای تخصیص‌یافته به خود را ببینید.',
            'message_en': 'You can only view progress of members assigned to you.',
        }
    profile = db.session.query(UserProfile).filter_by(user_id=member.id).first()
    weight = profile.weight if profile and profile.weight is not None else None
    height = profile.height if profile and profile.height is not None else None
    bmi = None
    if weight and height and height > 0:
        height_m = height / 100.0
        bmi = round(weight / (height_m * height_m), 1)
    limit = 10
    entries = db.session.query(ProgressEntry).filter_by(user_id=member.id)\
        .order_by(ProgressEntry.recorded_at.desc()).limit(limit).all()
    progress_entries = [{
        'weight_kg': e.weight_kg,
        'chest_cm': e.chest_cm,
        'waist_cm': e.waist_cm,
        'hips_cm': e.hips_cm,
        'recorded_at': e.recorded_at.isoformat() if e.recorded_at else None,
    } for e in entries]
    return {
        'action': 'get_member_progress',
        'status': 'ok',
        'data': {
            'member_id': member.id,
            'member_username': member.username or '',
            'member_name': member.username or '',
            'weight_kg': weight,
            'height_cm': height,
            'bmi': bmi,
            'progress_entries': progress_entries,
            'language': params.get('language') or language,
        },
    }


def _exec_get_dashboard_tab_info(params: Dict[str, Any], user: User, language: str) -> Dict[str, Any]:
    """Return info about Psychology Test or Online Laboratory dashboard tabs."""
    tab = (params.get('tab') or '').strip().lower()
    fa = language == 'fa'
    if tab == 'psychology-test':
        return {
            'action': 'get_dashboard_tab_info',
            'status': 'ok',
            'data': {
                'tab': 'psychology-test',
                'title_fa': 'تست روانشناسی',
                'title_en': 'Psychology Test',
                'description_fa': 'در این بخش سه تست روانشناسی ورزشی وجود دارد: ۱) ارزیابی شخصیت تمرینی (۱۵ سوال) ۲) هوش هیجانی در ورزش (۱۲ سوال) ۳) ارزیابی پتانسیل تمرینی (۱۲ سوال). هر تست پاسخ‌های چندگزینه‌ای دارد. پس از پاسخ به سوالات، نتیجه و امتیاز نمایش داده می‌شود. برای استفاده به داشبورد > تست روانشناسی بروید.',
                'description_en': 'This section has three sports psychology tests: 1) Exercise Personality Assessment (15 questions) 2) Emotional Intelligence in Sports (12 questions) 3) Exercise Potential Assessment (12 questions). Each test has multiple-choice answers. After answering, results and scores are shown. Go to Dashboard > Psychology Test to use it.',
            },
        }
    if tab == 'online-lab':
        return {
            'action': 'get_dashboard_tab_info',
            'status': 'ok',
            'data': {
                'tab': 'online-lab',
                'title_fa': 'آزمایشگاه آنلاین',
                'title_en': 'Online Laboratory',
                'description_fa': 'آزمایشگاه آنلاین شامل ماشین‌حساب‌های سلامتی است: BMI، درصد چربی بدن، وزن ایده‌آل، ضربان قلب استراحت، نیاز روزانه آب، یک‌حداکثر تکرار (RM)، اندازه قاب بدن، و BMR. فرم‌ها با اطلاعات پروفایل شما پیش‌پر می‌شوند. برای استفاده به داشبورد > آزمایشگاه آنلاین بروید.',
                'description_en': 'Online Laboratory includes health calculators: BMI, BFP, IBW, RHR, daily water needs, 1RM, frame size, and BMR. Forms are pre-filled with your profile data. Go to Dashboard > Online Laboratory to use it.',
            },
        }
    return {
        'action': 'get_dashboard_tab_info',
        'status': 'error',
        'error': 'invalid_tab',
        'message_fa': 'تب مورد نظر یافت نشد. لطفاً psychology-test یا online-lab را مشخص کنید.',
        'message_en': 'Tab not found. Please specify psychology-test or online-lab.',
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
