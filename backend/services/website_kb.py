"""
Website knowledge base (KB) - Real_State style.
Uses sqlite-vec + Vertex/OpenAI embeddings when SQLite (or WEBSITE_KB_VEC_DB).
When PostgreSQL: falls back to SQLAlchemy WebsiteKBChunk + Vertex/OpenAI embeddings + cosine similarity.
"""

import json
import logging
import math
import os

logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from flask import current_app

try:
    from services import vector_store
    HAS_VECTOR_STORE = True
except ImportError:
    try:
        from backend.services import vector_store
        HAS_VECTOR_STORE = True
    except ImportError:
        vector_store = None
        HAS_VECTOR_STORE = False


def _get_embedding_api_key() -> tuple:
    """Get Vertex or OpenAI API key from env or Admin AI Settings. Returns (key, provider)."""
    provider = (os.getenv("EMBEDDING_PROVIDER") or "vertex").strip().lower()
    if provider == "vertex":
        key = (os.getenv("VERTEX_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
        if key:
            return (key, "vertex")
        try:
            try:
                from services.ai_provider import get_provider_api_key, _get_settings
            except ImportError:
                from backend.services.ai_provider import get_provider_api_key, _get_settings
            st = _get_settings()
            for p in ("vertex", "gemini"):
                k, _ = get_provider_api_key(p, st)
                if k and isinstance(k, str) and k.strip():
                    return (k.strip(), "vertex")
        except Exception:
            pass
    else:
        key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if key:
            return (key, "openai")
        try:
            try:
                from services.ai_provider import get_provider_api_key, _get_settings
            except ImportError:
                from backend.services.ai_provider import get_provider_api_key, _get_settings
            k, _ = get_provider_api_key("openai", _get_settings())
            if k and isinstance(k, str) and k.strip():
                return (k.strip(), "openai")
        except Exception:
            pass
    return ("", provider)


def _embed_via_rest(text: str) -> List[float]:
    """Embed text via REST (Vertex/Gemini or OpenAI). Uses Admin AI Settings."""
    api_key, provider = _get_embedding_api_key()
    if not api_key:
        logger.error("[KB Embedding] No API key found. Set VERTEX_API_KEY or configure Vertex/Gemini in Admin.")
        raise RuntimeError(
            "Embedding API key required. Set VERTEX_API_KEY or GOOGLE_API_KEY, "
            "or configure Vertex/Gemini in Admin > AI Settings."
        )
    if provider == "vertex":
        model = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
        endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:predict"
        payload = {"instances": [{"content": text}]}
        r = requests.post(endpoint, params={"key": api_key}, json=payload, timeout=30)
        if r.status_code != 200:
            err = f"{r.status_code}: {r.text[:400]}" if r.text else str(r.status_code)
            logger.error("[KB Embedding] Vertex predict failed: %s", err)
            raise RuntimeError(f"Vertex embedding failed: {err}")
        resp = r

        data = resp.json()
        values = (data.get("embedding") or {}).get("values")
        if not values and data.get("predictions"):
            emb = data["predictions"][0].get("embeddings") or {}
            values = emb.get("values")
        if not values:
            raise RuntimeError("Vertex embedding response missing values.")
        return list(values)
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"model": model, "input": text}, timeout=30)
    resp.raise_for_status()
    items = (resp.json().get("data") or [])
    if not items:
        raise RuntimeError("OpenAI embedding response missing data.")
    return list((items[0].get("embedding") or []))


def _get_db():
    """Get SQLAlchemy from current Flask app context."""
    return current_app.extensions['sqlalchemy']


def _get_db_uri() -> str:
    return current_app.config.get('SQLALCHEMY_DATABASE_URI') or ''


def _use_sqlite_vec() -> bool:
    """True if we can use sqlite-vec (SQLite + extension available)."""
    if not HAS_VECTOR_STORE:
        return False
    uri = _get_db_uri()
    return vector_store.is_enabled(uri) if hasattr(vector_store, 'is_enabled') else False


def _generate_embedding(text: str) -> List[float]:
    """Use Vertex/OpenAI embeddings via REST."""
    if HAS_VECTOR_STORE and vector_store and hasattr(vector_store, 'embed_text'):
        return vector_store.embed_text(text)
    return _embed_via_rest(text)


def get_kb_source_text() -> str:
    """Build KB source from all website data: SiteSettings, Configuration, Exercises, Session phases. No manual editing."""
    db = _get_db()
    from models import SiteSettings, Configuration, Exercise

    parts: List[str] = []

    # --- Site Settings ---
    try:
        settings_row = db.session.query(SiteSettings).first()
        if settings_row:
            site_parts = []
            if settings_row.app_description_fa:
                site_parts.append(f"App description (fa): {settings_row.app_description_fa}")
            if settings_row.app_description_en:
                site_parts.append(f"App description (en): {settings_row.app_description_en}")
            if settings_row.contact_email:
                site_parts.append(f"Contact email: {settings_row.contact_email}")
            if settings_row.contact_phone:
                site_parts.append(f"Contact phone: {settings_row.contact_phone}")
            if settings_row.address_fa:
                site_parts.append(f"Address (fa): {settings_row.address_fa}")
            if settings_row.address_en:
                site_parts.append(f"Address (en): {settings_row.address_en}")
            for attr in ('instagram_url', 'telegram_url', 'whatsapp_url', 'copyright_text'):
                val = getattr(settings_row, attr, None)
                if val:
                    site_parts.append(f"{attr}: {val}")
            raw = getattr(settings_row, 'training_plans_products_json', None) or ''
            if raw and raw.strip():
                try:
                    data = json.loads(raw)
                    site_parts.append(f"Training plans/products: {json.dumps(data, ensure_ascii=False)[:3000]}")
                except json.JSONDecodeError:
                    pass
            # Session phases (warming, cooldown, ending)
            raw_phases = getattr(settings_row, 'session_phases_json', None) or ''
            if raw_phases and raw_phases.strip():
                try:
                    phases = json.loads(raw_phases)
                    phase_parts = []
                    for phase_key in ('warming', 'cooldown'):
                        p = phases.get(phase_key) or {}
                        if isinstance(p, dict):
                            t_fa = p.get('title_fa', '')
                            t_en = p.get('title_en', '')
                            steps = p.get('steps') or []
                            if t_fa or t_en:
                                phase_parts.append(f"{phase_key}: {t_fa} / {t_en}")
                            for s in steps[:10]:
                                if isinstance(s, dict):
                                    phase_parts.append(f"  step: {s.get('title_fa', '')} / {s.get('title_en', '')} - {s.get('description_fa', '')} / {s.get('description_en', '')}")
                                elif isinstance(s, str):
                                    phase_parts.append(f"  step: {s}")
                    em_fa = phases.get('ending_message_fa', '')
                    em_en = phases.get('ending_message_en', '')
                    if em_fa or em_en:
                        phase_parts.append(f"ending_message: {em_fa} / {em_en}")
                    if phase_parts:
                        site_parts.append("Session phases (warming, cooldown): " + " | ".join(phase_parts[:15]))
                except json.JSONDecodeError:
                    pass
            if site_parts:
                parts.append("## Site Settings\n" + "\n".join(site_parts))
    except Exception:
        pass

    # --- Configuration: Training Levels (with purposes) ---
    try:
        config_row = db.session.query(Configuration).first()
        if config_row and config_row.training_levels:
            try:
                levels = json.loads(config_row.training_levels)
                level_texts = []
                for key, val in (levels or {}).items():
                    if not isinstance(val, dict):
                        continue
                    desc_fa = val.get('description_fa', '')
                    desc_en = val.get('description_en', '')
                    goals = val.get('goals') or []
                    purposes = val.get('purposes') or {}
                    if desc_fa or desc_en:
                        level_texts.append(f"{key}: fa={desc_fa} en={desc_en}")
                    for g in goals:
                        if isinstance(g, dict):
                            level_texts.append(f"  goal: {g.get('en', '')} / {g.get('fa', '')}")
                        elif isinstance(g, str):
                            level_texts.append(f"  goal: {g}")
                    for purpose_key, purpose_val in purposes.items():
                        if isinstance(purpose_val, dict):
                            level_texts.append(
                                f"  purpose {purpose_key}: sessions={purpose_val.get('sessions_per_week')} "
                                f"sets={purpose_val.get('sets_per_action')} reps={purpose_val.get('reps_per_action')} "
                                f"focus_fa={purpose_val.get('training_focus_fa', '')} focus_en={purpose_val.get('training_focus_en', '')} "
                                f"break={purpose_val.get('break_between_sets')}"
                            )
                    level_texts.append("")
                if level_texts:
                    parts.append("## Training Levels Info\n" + "\n".join(level_texts))
            except json.JSONDecodeError:
                pass

        # --- Configuration: Injuries & Corrective Movements ---
        if config_row and config_row.injuries:
            try:
                injuries = json.loads(config_row.injuries)
                injury_texts = []
                for key, val in (injuries or {}).items():
                    if key.startswith('common_'):
                        injury_texts.append(f"{key}: {val}")
                        continue
                    if not isinstance(val, dict):
                        continue
                    fa = val.get('purposes_fa', '') or val.get('description_fa', '')
                    en = val.get('purposes_en', '') or val.get('description_en', '')
                    if fa or en:
                        injury_texts.append(f"{key}: fa={fa} en={en}")
                    for m in (val.get('allowed_movements') or []):
                        if isinstance(m, dict):
                            injury_texts.append(f"  allowed: {m.get('en', '')} / {m.get('fa', '')}")
                        elif isinstance(m, str):
                            injury_texts.append(f"  allowed: {m}")
                    for m in (val.get('forbidden_movements') or []):
                        if isinstance(m, dict):
                            injury_texts.append(f"  forbidden: {m.get('en', '')} / {m.get('fa', '')}")
                        elif isinstance(m, str):
                            injury_texts.append(f"  forbidden: {m}")
                    notes_fa = val.get('important_notes_fa', '')
                    notes_en = val.get('important_notes_en', '')
                    if notes_fa or notes_en:
                        injury_texts.append(f"  notes: {notes_fa} / {notes_en}")
                    injury_texts.append("")
                if injury_texts:
                    parts.append("## Injuries & Corrective Movements\n" + "\n".join(injury_texts))
            except json.JSONDecodeError:
                pass
    except Exception:
        pass

    # --- Exercise Library ---
    try:
        exercises = db.session.query(Exercise).order_by(Exercise.id).all()
        if exercises:
            ex_parts = []
            for ex in exercises:
                ex_parts.append(
                    f"Exercise: {ex.name_fa} / {ex.name_en} | "
                    f"target: {ex.target_muscle_fa} / {ex.target_muscle_en} | "
                    f"level={ex.level} intensity={ex.intensity} | "
                    f"tips_fa={ex.execution_tips_fa or ''} tips_en={ex.execution_tips_en or ''} | "
                    f"breathing_fa={ex.breathing_guide_fa or ''} breathing_en={ex.breathing_guide_en or ''} | "
                    f"equipment_fa={ex.equipment_needed_fa or ''} equipment_en={ex.equipment_needed_en or ''} | "
                    f"trainer_notes_fa={ex.trainer_notes_fa or ''} trainer_notes_en={ex.trainer_notes_en or ''} | "
                    f"injury_contraindications={ex.injury_contraindications or ''}"
                )
            if ex_parts:
                parts.append("## Exercise Library\n" + "\n".join(ex_parts))
    except Exception:
        pass

    return "\n\n".join(parts) if parts else ''


def trigger_kb_reindex_safe() -> bool:
    """Reindex KB after website content changes."""
    try:
        build_kb_index()
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("KB auto-reindex failed: %s", e)
        return False


def _chunk_text(text: str) -> List[str]:
    """Use same chunking as vector_store (800 chars, 120 overlap) for consistency."""
    if HAS_VECTOR_STORE and hasattr(vector_store, '_chunk_text'):
        return vector_store._chunk_text(text, chunk_size=800, overlap=120)
    if not text:
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    chunks: List[str] = []
    start, chunk_size, overlap = 0, 800, 120
    length = len(normalized)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(0, end - overlap)
    return chunks


def build_kb_index() -> Dict[str, Any]:
    """Build KB index. Uses sqlite-vec when SQLite, else SQLAlchemy WebsiteKBChunk. Vertex/OpenAI embeddings."""
    text = get_kb_source_text()
    logger.info("[KB Reindex] KB text length=%s chars, use_sqlite_vec=%s", len(text or ""), _use_sqlite_vec())

    if _use_sqlite_vec():
        uri = _get_db_uri()
        count, errors = vector_store.reindex_website_kb(uri, text)
        if errors:
            raise RuntimeError("; ".join(errors[:3]))
        return {
            'updated_at': datetime.utcnow().isoformat(),
            'count': count,
        }

    # PostgreSQL fallback: SQLAlchemy WebsiteKBChunk
    db = _get_db()
    from models import WebsiteKBChunk

    chunks = _chunk_text(text)
    db.session.query(WebsiteKBChunk).delete()
    db.session.commit()

    for idx, chunk in enumerate(chunks):
        embedding = _generate_embedding(chunk)
        row = WebsiteKBChunk(
            chunk_index=idx + 1,
            text=chunk,
            embedding_json=json.dumps(embedding),
        )
        db.session.add(row)
    db.session.commit()

    return {
        'updated_at': datetime.utcnow().isoformat(),
        'count': len(chunks),
    }


def load_kb_chunks() -> List[Dict[str, Any]]:
    """Load chunks (PostgreSQL path only)."""
    db = _get_db()
    from models import WebsiteKBChunk

    rows = db.session.query(WebsiteKBChunk).order_by(WebsiteKBChunk.chunk_index).all()
    result = []
    for r in rows:
        try:
            emb = json.loads(r.embedding_json) if r.embedding_json else []
        except json.JSONDecodeError:
            emb = []
        result.append({
            'id': r.chunk_index,
            'text': r.text or '',
            'embedding': emb,
        })
    return result


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_kb(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search KB. Uses sqlite-vec when SQLite, else cosine on SQLAlchemy chunks. Vertex/OpenAI embeddings."""
    if _use_sqlite_vec():
        uri = _get_db_uri()
        texts = vector_store.search_website_kb(uri, query, limit=max(1, min(top_k, 10)))
        return [{'score': 1.0, 'text': t, 'id': i + 1} for i, t in enumerate(texts)]

    chunks = load_kb_chunks()
    if not chunks:
        return []

    try:
        q_embed = _generate_embedding(query)
    except Exception:
        return []

    scored = []
    for ch in chunks:
        score = _cosine_similarity(q_embed, ch.get('embedding') or [])
        scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {'score': float(s), 'text': ch.get('text', ''), 'id': ch.get('id')}
        for s, ch in scored[:max(1, min(top_k, 10))]
    ]


def get_kb_status() -> Dict[str, Any]:
    """Return KB status (count, updated_at)."""
    if _use_sqlite_vec():
        uri = _get_db_uri()
        count = vector_store.get_website_kb_count(uri)
        return {
            'count': count,
            'updated_at': datetime.utcnow().isoformat() if count else None,
        }

    db = _get_db()
    from models import WebsiteKBChunk

    count = db.session.query(WebsiteKBChunk).count()
    last = db.session.query(WebsiteKBChunk).order_by(WebsiteKBChunk.updated_at.desc()).first()
    return {
        'count': count,
        'updated_at': last.updated_at.isoformat() if last and last.updated_at else None,
    }
