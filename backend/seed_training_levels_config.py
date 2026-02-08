"""
Seed the Configuration table with Training Level Info and Corrective Movements data
from the Excel/export script, so the admin "Training Level Info" tab shows all content.

Run from project root: python backend/seed_training_levels_config.py
Or from backend: python seed_training_levels_config.py
"""
import os
import sys
import json

# Ensure backend and project root are on path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import data from the export script (same as Excel)
from scripts.export_training_levels_docs import (
    TRAINING_LEVELS_DATA,
    INJURIES_DATA,
    COMMON_INJURY_NOTE,
)


def build_training_levels_payload():
    """Build JSON payload for training_levels as stored by admin API."""
    out = {}
    for level_key in ('beginner', 'intermediate', 'advanced'):
        data = TRAINING_LEVELS_DATA.get(level_key, {})
        goals = data.get('goals', [])
        out[level_key] = {
            'description_fa': data.get('description_fa', ''),
            'description_en': data.get('description_en', ''),
            'goals': [{'fa': g.get('fa', ''), 'en': g.get('en', '')} for g in goals],
            'purposes': data.get('purposes', {}),
        }
    return out


def build_injuries_payload():
    """Build JSON payload for injuries as stored by admin API."""
    injury_keys = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle']
    out = {}
    for key in injury_keys:
        data = INJURIES_DATA.get(key, {})
        out[key] = {
            'purposes_fa': data.get('purposes_fa', ''),
            'purposes_en': data.get('purposes_en', ''),
            'allowed_movements': [{'fa': m.get('fa', ''), 'en': m.get('en', '')} for m in data.get('allowed_movements', [])],
            'forbidden_movements': [{'fa': m.get('fa', ''), 'en': m.get('en', '')} for m in data.get('forbidden_movements', [])],
            'important_notes_fa': data.get('important_notes_fa', ''),
            'important_notes_en': data.get('important_notes_en', ''),
        }
    out['common_injury_note_fa'] = COMMON_INJURY_NOTE.get('fa', '')
    out['common_injury_note_en'] = COMMON_INJURY_NOTE.get('en', '')
    return out


def seed():
    from app import app, db
    from models import Configuration

    with app.app_context():
        training_levels = build_training_levels_payload()
        injuries = build_injuries_payload()

        config = db.session.query(Configuration).first()
        if not config:
            config = Configuration()
            db.session.add(config)

        config.training_levels = json.dumps(training_levels, ensure_ascii=False)
        config.injuries = json.dumps(injuries, ensure_ascii=False)

        db.session.commit()
        print('Configuration seeded: Training Level Info and Corrective Movements (from Excel data).')
        print('Open Admin Dashboard > Training Level Info tab to see the content.')


if __name__ == '__main__':
    seed()
