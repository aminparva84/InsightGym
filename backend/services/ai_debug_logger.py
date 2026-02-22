"""
AI debug CSV logger for testing. Logs each chat request to backend/logs/ai_debug.csv.
Enabled by default. Set AI_DEBUG_CSV=false to disable. Path configurable via AI_DEBUG_CSV_PATH.
"""

import csv
import json
import os
from datetime import datetime


def _get_log_dir():
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def _get_csv_path():
    return os.getenv("AI_DEBUG_CSV_PATH") or os.path.join(_get_log_dir(), "ai_debug.csv")


def _ensure_header(path):
    """Ensure file exists with header. If file is new, write header."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "message", "response", "action_json", "error"])


def _compact_action_json(obj: dict) -> dict:
    """Create a compact version for logging - strip heavy session/exercise data from plans."""
    if not obj:
        return obj
    out = {}
    for k, v in obj.items():
        if k == "results" and isinstance(v, list):
            compact_results = []
            for r in v:
                if not isinstance(r, dict):
                    compact_results.append(r)
                    continue
                cr = dict(r)
                if r.get("action") == "suggest_training_plans" and r.get("status") == "ok":
                    data = cr.get("data") or {}
                    plans = data.get("plans") or []
                    if plans:
                        data = dict(data)
                        data["plans"] = [
                            {"id": p.get("id"), "name_fa": p.get("name_fa"), "name_en": p.get("name_en"), "price": p.get("price"), "session_count": len(p.get("sessions") or [])}
                            for p in plans
                        ]
                        data["_summary"] = f"Suggested {len(plans)} plan(s): " + ", ".join(p.get("name_fa") or p.get("name_en") or "" for p in plans)
                        cr["data"] = data
                compact_results.append(cr)
            out[k] = compact_results
        else:
            out[k] = v
    return out


def append_log(message: str, response: str, action_json: dict, error: str = ""):
    """Append one row to ai_debug.csv. Set AI_DEBUG_CSV=false to disable (default: enabled for testing).
    Plans data is compacted (sessions stripped) to keep logs readable.
    Also writes to ai_debug.jsonl (one JSON per line) for easier viewing."""
    if str(os.getenv("AI_DEBUG_CSV", "true")).lower() in ("0", "false", "no"):
        return
    compact = _compact_action_json(action_json or {})
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_iso = datetime.utcnow().isoformat() + "Z"
    try:
        path = _get_csv_path()
        _ensure_header(path)
        with open(path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                (message or "")[:500],
                (response or "")[:1000],
                json.dumps(compact, ensure_ascii=False),
                (error or "")[:500],
            ])
    except Exception as e:
        print(f"[ai_debug_logger] Failed to write CSV log: {e}", flush=True)
    try:
        jsonl_path = os.path.join(_get_log_dir(), "ai_debug.jsonl")
        entry = {
            "timestamp": timestamp_iso,
            "message": (message or "")[:500],
            "response": (response or "")[:1000],
            "action_json": compact,
            "error": (error or "")[:500],
        }
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[ai_debug_logger] Failed to write JSONL log: {e}", flush=True)


def append_ai_program_log(
    action: str,
    user_id: int,
    program_id: int,
    template_name: str = "",
    purpose: str = "",
    profile_summary: str = "",
    sessions_count: int = 0,
    assigned_program_id: int = 0,
    error: str = "",
    **kwargs,
):
    """
    Log AI-designed program action to ai_debug.csv.
    action: 'ai_generated' | 'template_copy' | 'generate_next_sessions' | 'generate_next_sessions_failed'
    Extra kwargs (e.g. start_session_index) are merged into action_json.
    """
    if str(os.getenv("AI_DEBUG_CSV", "true")).lower() in ("0", "false", "no"):
        return
    message = f"AI-designed program | user_id={user_id} program_id={program_id}"
    response = "AI-generated" if action == "ai_generated" else (
        "Fallback: template copy" if action == "template_copy" else action
    )
    action_json = {
        "action": action,
        "user_id": user_id,
        "program_id": program_id,
        "template_name": template_name,
        "purpose": purpose,
        "profile_summary": (profile_summary or "")[:500],
        "sessions_count": sessions_count,
        "assigned_program_id": assigned_program_id,
        **{k: v for k, v in kwargs.items() if v is not None and v != ""},
    }
    append_log(message, response, action_json, error or "")
