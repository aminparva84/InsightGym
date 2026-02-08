"""
Action planner service for AI-driven actions with strict JSON output.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app import db, User, TrainerMessage
from models import Exercise, UserProfile, SiteSettings, ProgressCheckRequest
from services.ai_provider import chat_completion
from services.website_kb import search_kb
from services.ai_coach_agent import PersianFitnessCoachAI


ALLOWED_ACTIONS = (
    'search_exercises',
    'create_workout_plan',
    'update_user_profile',
    'progress_check',
    'trainer_message',
    'site_settings',
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


def _build_prompt(message: str, language: str, role: str) -> Tuple[str, str]:
    system = (
        "You are an action planner for a fitness platform. "
        "Return ONLY valid JSON with keys: assistant_response (string) and actions (array). "
        "Each action must be an object with keys: action (string), params (object). "
        "Allowed actions: "
        "search_exercises, create_workout_plan, update_user_profile, "
        "progress_check, trainer_message, site_settings. "
        "Do not include markdown or explanations. "
        "If no action is needed, return an empty actions array."
    )
    user = (
        f"UserRole: {role}\n"
        f"Language: {language}\n"
        f"Message: {message}\n"
        "Action schemas:\n"
        "- search_exercises: params { query?, target_muscle?, level?, intensity?, max_results?, language? }\n"
        "- create_workout_plan: params { month?, target_muscle?, language? }\n"
        "- update_user_profile: params { user_id?, fields (object) }\n"
        "- progress_check: params { mode ('request'|'respond'), request_id?, status? }\n"
        "- trainer_message: params { recipient_id?, body }\n"
        "- site_settings: params { fields (object) }\n"
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
    system, user_msg = _build_prompt(message, language, getattr(user, 'role', 'member') or 'member')
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


def plan_and_execute(message: str, user: User, language: str) -> Dict[str, Any]:
    plan = plan_actions(message, user, language)
    results = execute_actions(plan.get('actions', []), user, language)
    return {
        'assistant_response': plan.get('assistant_response'),
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


def execute_actions(actions: List[Dict[str, Any]], user: User, language: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for action_item in actions:
        action = action_item.get('action')
        params = action_item.get('params') or {}
        try:
            if action == 'search_exercises':
                results.append(_exec_search_exercises(params, user, language))
            elif action == 'create_workout_plan':
                results.append(_exec_create_workout_plan(params, user, language))
            elif action == 'update_user_profile':
                results.append(_exec_update_user_profile(params, user, language))
            elif action == 'progress_check':
                results.append(_exec_progress_check(params, user, language))
            elif action == 'trainer_message':
                results.append(_exec_trainer_message(params, user, language))
            elif action == 'site_settings':
                results.append(_exec_site_settings(params, user, language))
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

    user_profile = UserProfile.query.filter_by(user_id=user.id).first()
    q = Exercise.query
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

    coach = PersianFitnessCoachAI(user.id)
    user_injuries = coach.user_profile.get_injuries() if coach.user_profile else []
    q = Exercise.query
    if coach.user_profile and not coach.user_profile.gym_access:
        q = q.filter(Exercise.category == 'functional_home')
    exercise_pool = q.limit(50).all()
    plan = coach._handle_workout_plan_request(message, month, user_injuries, exercise_pool)
    return {
        'action': 'create_workout_plan',
        'status': 'ok',
        'data': plan,
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

    profile = UserProfile.query.filter_by(user_id=target_user_id).first()
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
        req = ProgressCheckRequest.query.filter_by(id=request_id).first()
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
    row = SiteSettings.query.first()
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
