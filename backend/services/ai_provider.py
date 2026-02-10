"""
Unified AI provider service: OpenAI, Anthropic, Gemini, Vertex AI.
Uses admin-configured API keys and selected provider from SiteSettings.ai_settings_json.
Vertex AI uses the REST API only (aiplatform.googleapis.com), no SDK.
"""

import os
import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

PROVIDERS = ('openai', 'anthropic', 'gemini', 'vertex')
SELECTED_DEFAULT = 'auto'  # Use first available valid provider when not chosen by admin

# Lazy app/settings access to avoid circular import
def _get_settings() -> Dict[str, Any]:
    """Load ai_settings_json from SiteSettings. Returns dict with selected_provider and per-provider keys."""
    try:
        from app import db
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        raw = getattr(row, 'ai_settings_json', None) or ''
        if not raw or not raw.strip():
            return {'selected_provider': SELECTED_DEFAULT}
        data = json.loads(raw)
        if not data.get('selected_provider'):
            data['selected_provider'] = SELECTED_DEFAULT
        return data
    except Exception as e:
        print(f"ai_provider: could not load settings: {e}")
        return {'selected_provider': SELECTED_DEFAULT}


def _save_settings(settings: Dict[str, Any]) -> bool:
    try:
        from app import db
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        if not row:
            row = SiteSettings()
            db.session.add(row)
        row.ai_settings_json = json.dumps(settings, ensure_ascii=False)
        db.session.commit()
        return True
    except Exception as e:
        print(f"ai_provider: could not save settings: {e}")
        if db and getattr(db, 'session', None):
            db.session.rollback()
        return False


def get_provider_api_key(provider: str, settings: Optional[Dict] = None) -> Tuple[Optional[str], str]:
    """
    Return (api_key or None, source).
    source: 'database' | 'environment' | ''
    """
    if settings is None:
        settings = _get_settings()
    key = None
    source = ''
    if provider == 'openai':
        key = (settings.get('openai') or {}).get('api_key') or os.getenv('OPENAI_API_KEY')
        source = 'database' if (settings.get('openai') or {}).get('api_key') else ('environment' if os.getenv('OPENAI_API_KEY') else '')
    elif provider == 'anthropic':
        key = (settings.get('anthropic') or {}).get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        source = 'database' if (settings.get('anthropic') or {}).get('api_key') else ('environment' if os.getenv('ANTHROPIC_API_KEY') else '')
    elif provider == 'gemini':
        key = (settings.get('gemini') or {}).get('api_key') or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        source = 'database' if (settings.get('gemini') or {}).get('api_key') else ('environment' if (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')) else '')
    elif provider == 'vertex':
        key = (settings.get('vertex') or {}).get('api_key') or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        source = 'database' if (settings.get('vertex') or {}).get('api_key') else ('environment' if (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')) else '')
    return (key.strip() if key and isinstance(key, str) else None, source)


def is_sdk_installed(provider: str) -> bool:
    if provider == 'openai':
        try:
            import openai
            return True
        except ImportError:
            return False
    if provider == 'anthropic':
        try:
            import anthropic
            return True
        except ImportError:
            return False
    if provider == 'gemini':
        try:
            import google.generativeai
            return True
        except ImportError:
            return False
    if provider == 'vertex':
        return True  # Vertex uses REST API only, no SDK required
    return False


def _resolve_provider(settings: Dict[str, Any]) -> Optional[str]:
    """Resolve selected_provider to a concrete provider. Returns first available when 'auto'."""
    chosen = (settings.get('selected_provider') or SELECTED_DEFAULT).lower()
    if chosen == 'auto':
        for p in PROVIDERS:
            key, _ = get_provider_api_key(p, settings)
            if key and is_sdk_installed(p):
                return p
        return None
    if chosen in PROVIDERS:
        return chosen
    return None


def chat_completion(system: str, user_message: str, max_tokens: int = 800) -> Optional[str]:
    """
    Call the selected AI provider (from settings). Returns response text or None on failure.
    When selected_provider is 'auto', uses the first available valid provider.
    """
    settings = _get_settings()
    provider = _resolve_provider(settings)
    if not provider:
        print("ai_provider: no provider available (auto: none configured, or selected has no key/SDK)")
        return None
    api_key, _ = get_provider_api_key(provider, settings)
    if not api_key:
        print("ai_provider: no API key for provider", provider)
        return None
    if not is_sdk_installed(provider):
        print("ai_provider: SDK not installed for", provider)
        return None

    try:
        if provider == 'openai':
            return _openai_chat(api_key, system, user_message, max_tokens)
        if provider == 'anthropic':
            return _anthropic_chat(api_key, system, user_message, max_tokens)
        if provider == 'gemini':
            return _gemini_chat(api_key, system, user_message, max_tokens)
        if provider == 'vertex':
            return _vertex_chat(api_key, system, user_message, max_tokens)
    except Exception as e:
        print(f"ai_provider chat error ({provider}): {e}")
    return None


def _openai_chat(api_key: str, system: str, user_message: str, max_tokens: int) -> Optional[str]:
    try:
        import openai
        client = getattr(openai, 'OpenAI', None)
        if client:
            c = client(api_key=api_key)
            r = c.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user_message},
                ],
                max_tokens=max_tokens,
            )
            if r.choices and len(r.choices) > 0:
                content = getattr(r.choices[0], 'message', None)
                if content:
                    return (getattr(content, 'content', None) or '').strip()
            return ''
        openai.api_key = api_key
        if hasattr(openai, 'ChatCompletion'):
            r = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user_message},
                ],
                max_tokens=max_tokens,
            )
            return (r.choices or [{}])[0].get('message', {}).get('content', '').strip()
    except Exception as e:
        print(f"OpenAI chat error: {e}")
        raise
    return None


def _anthropic_chat(api_key: str, system: str, user_message: str, max_tokens: int) -> Optional[str]:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    m = client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=max_tokens,
        system=system,
        messages=[{'role': 'user', 'content': user_message}],
    )
    if m.content and len(m.content) > 0:
        block = m.content[0]
        if getattr(block, 'text', None):
            return block.text.strip()
    return None


def _gemini_chat(api_key: str, system: str, user_message: str, max_tokens: int) -> Optional[str]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"{system}\n\nUser: {user_message}"
    r = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens))
    if r and r.text:
        return r.text.strip()
    return None


# Vertex AI REST API (API key only); model name configurable via env
VERTEX_MODEL = os.getenv('VERTEX_AI_MODEL', 'gemini-2.5-flash-lite')
VERTEX_BASE = 'https://aiplatform.googleapis.com/v1/publishers/google/models'


def _vertex_chat(api_key: str, system: str, user_message: str, max_tokens: int) -> Optional[str]:
    """
    Vertex AI via REST API only (aiplatform.googleapis.com).
    Uses API key in query param; model: gemini-2.5-flash-lite (or VERTEX_AI_MODEL).
    """
    qs = urllib.parse.urlencode({"key": api_key})
    url = f"{VERTEX_BASE}/{VERTEX_MODEL}:generateContent?{qs}"
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system}\n\n{user_message}".strip()}],
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
        },
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8') if e.fp else ''
        raise RuntimeError(f"Vertex API error {e.code}: {raw}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Vertex API request failed: {e.reason}")

    # Parse response: candidates[0].content.parts[0].text
    candidates = data.get("candidates") or []
    if not candidates:
        block = data.get("promptFeedback") or {}
        raise RuntimeError(block.get("blockReasonMessage") or "No candidates in response")
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    if not parts:
        return None
    return (parts[0].get("text") or "").strip()


def test_provider(provider: str, api_key_override: Optional[str] = None) -> Tuple[bool, str]:
    """
    Test the given provider with optional api_key. Returns (success, message).
    On success, updates last_tested_at and is_valid in settings.
    """
    if provider not in PROVIDERS:
        return False, f"Unknown provider: {provider}"
    if not is_sdk_installed(provider):
        return False, "SDK not installed"
    settings = _get_settings()
    api_key = api_key_override or get_provider_api_key(provider, settings)[0]
    if not api_key:
        return False, "No API key set"
    test_system = "You are a test. Reply only with OK."
    test_user = "Say OK."
    try:
        if provider == 'openai':
            out = _openai_chat(api_key, test_system, test_user, 50)
        elif provider == 'anthropic':
            out = _anthropic_chat(api_key, test_system, test_user, 50)
        elif provider == 'gemini':
            out = _gemini_chat(api_key, test_system, test_user, 50)
        else:
            out = _vertex_chat(api_key, test_system, test_user, 50)
        if out and 'ok' in out.lower():
            # Update settings: last_tested_at, is_valid
            key = provider
            if key not in settings:
                settings[key] = {}
            settings[key]['last_tested_at'] = datetime.utcnow().isoformat()
            settings[key]['is_valid'] = True
            if not api_key_override:
                _save_settings(settings)
            return True, "API key is valid"
        return False, "Unexpected response"
    except Exception as e:
        msg = str(e)
        key = provider
        if key not in settings:
            settings[key] = {}
        settings[key]['last_tested_at'] = datetime.utcnow().isoformat()
        settings[key]['is_valid'] = False
        if not api_key_override:
            _save_settings(settings)
        return False, msg


def get_embedding_api_key() -> Optional[str]:
    """Return API key for embeddings (OpenAI). Uses AI settings OpenAI key or env."""
    key, _ = get_provider_api_key('openai')
    return key
