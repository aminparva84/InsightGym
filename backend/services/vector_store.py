"""
Vector store for Website KB - REST only (no SDKs).
Uses sqlite-vec + Vertex/Gemini or OpenAI embeddings via REST API.
"""

import json
import os
import sqlite3
import requests
from typing import List, Optional, Tuple

try:
    import sqlite_vec
    HAS_SQLITE_VEC = True
except ImportError:
    sqlite_vec = None
    HAS_SQLITE_VEC = False


EMBEDDING_PROVIDER = (os.getenv("EMBEDDING_PROVIDER") or "vertex").strip().lower()
DEFAULT_EMBEDDING_MODEL = (
    os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    if EMBEDDING_PROVIDER == "vertex"
    else os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
)
DEFAULT_EMBEDDING_DIM = int(os.getenv("VECTOR_EMBEDDING_DIM", "768" if EMBEDDING_PROVIDER == "vertex" else "1536"))


def _sqlite_db_path(db_uri: str) -> Optional[str]:
    kb_path = (os.getenv("WEBSITE_KB_VEC_DB") or "").strip()
    if kb_path:
        if not os.path.isabs(kb_path):
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base, kb_path)
        return kb_path
    if not db_uri or not db_uri.startswith("sqlite:///"):
        return None
    path = db_uri.replace("sqlite:///", "")
    if not os.path.isabs(path):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, path)
    return path


def _load_vec_extension(conn: sqlite3.Connection) -> None:
    if not HAS_SQLITE_VEC:
        raise RuntimeError("sqlite-vec not installed. Run: pip install sqlite-vec")
    if hasattr(conn, "enable_load_extension"):
        conn.enable_load_extension(True)
    if sqlite_vec and hasattr(sqlite_vec, "load"):
        sqlite_vec.load(conn)
        return
    path = (os.getenv("SQLITE_VEC_PATH") or "").strip()
    if not path:
        raise RuntimeError("SQLITE_VEC_PATH not set and sqlite_vec.load unavailable.")
    conn.load_extension(path)


def _serialize_vector(vec: List[float]) -> object:
    if sqlite_vec and hasattr(sqlite_vec, "serialize"):
        try:
            return sqlite_vec.serialize(vec)
        except Exception:
            pass
    return json.dumps(vec)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS website_kb_chunks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "content TEXT NOT NULL)"
    )
    conn.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS website_kb_embeddings "
        f"USING vec0(embedding float[{DEFAULT_EMBEDDING_DIM}], chunk_id INTEGER)"
    )
    conn.commit()


def _connect(db_uri: str) -> sqlite3.Connection:
    db_path = _sqlite_db_path(db_uri)
    if not db_path:
        raise RuntimeError(
            "Vector store requires SQLite. Use DATABASE_URL=sqlite:///... or set "
            "WEBSITE_KB_VEC_DB=instance/website_kb_vec.db"
        )
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    _load_vec_extension(conn)
    _ensure_schema(conn)
    return conn


def is_enabled(db_uri: str) -> bool:
    if not HAS_SQLITE_VEC:
        return False
    if not _sqlite_db_path(db_uri):
        return False
    try:
        conn = _connect(db_uri)
        conn.close()
        return True
    except Exception:
        return False


def _get_vertex_api_key() -> str:
    """Get Vertex/Gemini API key from env or Admin AI Settings."""
    api_key = (os.getenv("VERTEX_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
    if api_key:
        return api_key
    try:
        from services.ai_provider import get_provider_api_key, _get_settings
        st = _get_settings()
        for p in ("vertex", "gemini"):
            key, _ = get_provider_api_key(p, st)
            if key:
                return key or ""
    except Exception:
        pass
    return ""


def _embed_vertex_rest(text: str) -> List[float]:
    """Vertex AI embeddings via REST - exactly like Real_State (no project_id)."""
    api_key = _get_vertex_api_key()
    if not api_key:
        raise RuntimeError(
            "Vertex API key required. Set VERTEX_API_KEY or GOOGLE_API_KEY, "
            "or configure Vertex in Admin > AI Settings."
        )
    endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{DEFAULT_EMBEDDING_MODEL}:predict"
    payload = {"instances": [{"content": text}]}
    resp = requests.post(endpoint, params={"key": api_key}, json=payload, timeout=30)
    resp.raise_for_status()
    body = resp.json()
    predictions = body.get("predictions") or []
    if not predictions:
        raise RuntimeError("No embedding returned from Vertex.")
    embedding = predictions[0].get("embeddings") or {}
    values = embedding.get("values")
    if not values:
        raise RuntimeError("Vertex embedding response missing values.")
    return list(values)


def _get_openai_api_key() -> str:
    """Get OpenAI API key from env or Admin AI Settings."""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if api_key:
        return api_key
    try:
        from services.ai_provider import get_provider_api_key, _get_settings
        key, _ = get_provider_api_key("openai", _get_settings())
        return key or ""
    except Exception:
        pass
    return ""


def _embed_openai_rest(text: str) -> List[float]:
    """OpenAI embeddings via REST."""
    api_key = _get_openai_api_key()
    if not api_key:
        raise RuntimeError(
            "OpenAI API key required. Set OPENAI_API_KEY or configure OpenAI in Admin > AI Settings."
        )
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": DEFAULT_EMBEDDING_MODEL, "input": text}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data") or []
    if not items:
        raise RuntimeError("OpenAI embedding response missing data.")
    return list(items[0].get("embedding") or [])


def embed_text(text: str) -> List[float]:
    """Embed text using Vertex or OpenAI via REST only."""
    if EMBEDDING_PROVIDER == "vertex":
        return _embed_vertex_rest(text)
    return _embed_openai_rest(text)


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    if not text:
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    chunks = []
    start = 0
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


def reindex_website_kb(db_uri: str, kb_text: str) -> Tuple[int, List[str]]:
    errors: List[str] = []
    if not kb_text or not kb_text.strip():
        return 0, ["KB text is empty."]
    chunks = _chunk_text(kb_text)
    if not chunks:
        return 0, ["No chunks produced from KB text."]

    if not _sqlite_db_path(db_uri):
        return 0, ["Vector store requires SQLite. Use DATABASE_URL=sqlite:///... or WEBSITE_KB_VEC_DB."]

    conn = _connect(db_uri)
    try:
        conn.execute("DELETE FROM website_kb_chunks")
        conn.execute("DELETE FROM website_kb_embeddings")
        conn.commit()

        for chunk in chunks:
            try:
                vector = embed_text(chunk)
                if len(vector) != DEFAULT_EMBEDDING_DIM:
                    raise RuntimeError(f"Embedding dimension mismatch: {len(vector)} != {DEFAULT_EMBEDDING_DIM}")
                cursor = conn.execute(
                    "INSERT INTO website_kb_chunks (content) VALUES (?)",
                    (chunk,)
                )
                chunk_id = cursor.lastrowid
                conn.execute(
                    "INSERT INTO website_kb_embeddings (chunk_id, embedding) VALUES (?, ?)",
                    (chunk_id, _serialize_vector(vector))
                )
            except Exception as e:
                errors.append(str(e))
        conn.commit()
        return len(chunks), errors
    finally:
        conn.close()


def search_website_kb(db_uri: str, query_text: str, limit: int = 4) -> List[str]:
    if not query_text or not query_text.strip():
        return []
    if not _sqlite_db_path(db_uri):
        return []

    vector = embed_text(query_text)
    if len(vector) != DEFAULT_EMBEDDING_DIM:
        return []

    conn = _connect(db_uri)
    try:
        cursor = conn.execute(
            "SELECT chunk_id FROM website_kb_embeddings "
            "WHERE embedding MATCH ? "
            "ORDER BY distance "
            "LIMIT ?",
            (_serialize_vector(vector), limit)
        )
        ids = [row[0] for row in cursor.fetchall() if row and row[0] is not None]
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT content FROM website_kb_chunks WHERE id IN ({placeholders})",
            tuple(ids)
        ).fetchall()
        return [row[0] for row in rows if row and row[0]]
    finally:
        conn.close()


def get_website_kb_count(db_uri: str) -> int:
    if not _sqlite_db_path(db_uri):
        return 0
    try:
        conn = _connect(db_uri)
        try:
            row = conn.execute("SELECT COUNT(*) FROM website_kb_chunks").fetchone()
            return row[0] if row else 0
        finally:
            conn.close()
    except Exception:
        return 0
