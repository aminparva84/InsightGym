"""
AI debug CSV logger for testing. Logs each chat request to backend/logs/ai_debug.csv.
Enabled by default. Set AI_DEBUG_CSV=false to disable. Path configurable via AI_DEBUG_CSV_PATH.
"""

import csv
import json
import os


def _get_csv_path():
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    return os.getenv("AI_DEBUG_CSV_PATH") or os.path.join(log_dir, "ai_debug.csv")


def _ensure_header(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["message", "response", "action_json", "error"])


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
    Plans data is compacted (sessions stripped) to keep logs readable."""
    if str(os.getenv("AI_DEBUG_CSV", "true")).lower() in ("0", "false", "no"):
        return
    try:
        compact = _compact_action_json(action_json or {})
        path = _get_csv_path()
        _ensure_header(path)
        with open(path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                message or "",
                response or "",
                json.dumps(compact, ensure_ascii=False),
                error or "",
            ])
    except Exception:
        pass


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
):
    """
    Log AI-designed program action to ai_debug.csv.
    action: 'ai_generated' | 'template_copy'
    """
    if str(os.getenv("AI_DEBUG_CSV", "true")).lower() in ("0", "false", "no"):
        return
    message = f"AI-designed program after purchase | user_id={user_id} program_id={program_id}"
    response = "AI-generated" if action == "ai_generated" else "Fallback: template copy"
    action_json = {
        "action": action,
        "user_id": user_id,
        "program_id": program_id,
        "template_name": template_name,
        "purpose": purpose,
        "profile_summary": (profile_summary or "")[:500],
        "sessions_count": sessions_count,
        "assigned_program_id": assigned_program_id,
    }
    append_log(message, response, action_json, error or "")
