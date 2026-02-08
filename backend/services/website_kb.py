"""
Website knowledge base (KB) indexing and search.
Stores embeddings in a local JSON index file.
"""

import json
import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.ai_provider import get_embedding_api_key


_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KB_SOURCE_PATH = os.path.join(_BASE_DIR, 'website_kb_source.md')
KB_INDEX_PATH = os.path.join(_BASE_DIR, 'website_kb_index.json')


def _read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def _write_file(path: str, content: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_kb_source_text() -> str:
    base_text = _read_file(KB_SOURCE_PATH)
    # Append site settings for additional context (best-effort)
    try:
        from app import db
        from models import SiteSettings
        row = db.session.query(SiteSettings).first()
        if row:
            parts = []
            if row.app_description_fa:
                parts.append(f"App description (fa): {row.app_description_fa}")
            if row.app_description_en:
                parts.append(f"App description (en): {row.app_description_en}")
            if row.contact_email:
                parts.append(f"Contact email: {row.contact_email}")
            if row.contact_phone:
                parts.append(f"Contact phone: {row.contact_phone}")
            if row.address_fa:
                parts.append(f"Address (fa): {row.address_fa}")
            if row.address_en:
                parts.append(f"Address (en): {row.address_en}")
            if parts:
                base_text = (base_text or '') + "\n\n" + "\n".join(parts)
    except Exception:
        pass
    return base_text or ''


def save_kb_source_text(content: str) -> None:
    _write_file(KB_SOURCE_PATH, content or '')


def _chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks: List[str] = []
    current = ''
    for p in paragraphs:
        if len(current) + len(p) + 1 <= max_chars:
            current = f"{current}\n{p}".strip()
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_chars:
                current = p
            else:
                # Hard split long paragraph
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i:i + max_chars])
                current = ''
    if current:
        chunks.append(current)

    # Add overlap
    if overlap > 0 and len(chunks) > 1:
        overlapped = []
        for i, ch in enumerate(chunks):
            if i == 0:
                overlapped.append(ch)
                continue
            prev = chunks[i - 1]
            tail = prev[-overlap:] if len(prev) > overlap else prev
            overlapped.append((tail + "\n" + ch).strip())
        return overlapped
    return chunks


def _generate_embedding(text: str) -> List[float]:
    key = get_embedding_api_key()
    if not key:
        raise ValueError("No OpenAI API key configured for embeddings.")
    try:
        import openai
        client = getattr(openai, 'OpenAI', None)
        if client:
            c = client(api_key=key)
            response = c.embeddings.create(
                model='text-embedding-3-small',
                input=text,
                dimensions=1536
            )
            return response.data[0].embedding
        openai.api_key = key
        response = openai.embeddings.create(
            model='text-embedding-3-small',
            input=text,
            dimensions=1536
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Error generating embedding: {e}")


def build_kb_index() -> Dict[str, Any]:
    text = get_kb_source_text()
    chunks = _chunk_text(text)
    index_chunks = []
    for idx, chunk in enumerate(chunks):
        embedding = _generate_embedding(chunk)
        index_chunks.append({
            'id': idx + 1,
            'text': chunk,
            'embedding': embedding,
        })
    payload = {
        'updated_at': datetime.utcnow().isoformat(),
        'count': len(index_chunks),
        'chunks': index_chunks,
    }
    _write_file(KB_INDEX_PATH, json.dumps(payload, ensure_ascii=False))
    return payload


def load_kb_index() -> Optional[Dict[str, Any]]:
    raw = _read_file(KB_INDEX_PATH)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


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
    index = load_kb_index()
    if not index or not index.get('chunks'):
        return []
    try:
        q_embed = _generate_embedding(query)
    except Exception:
        return []
    scored = []
    for ch in index.get('chunks', []):
        score = _cosine_similarity(q_embed, ch.get('embedding') or [])
        scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, ch in scored[:max(1, min(top_k, 10))]:
        results.append({
            'score': score,
            'text': ch.get('text', ''),
            'id': ch.get('id'),
        })
    return results
