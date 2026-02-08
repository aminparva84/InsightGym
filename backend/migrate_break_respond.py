"""
Migration: Add responded_at and response_message to break_requests for accept/deny.
Run with: python migrate_break_respond.py
DB-agnostic: uses SQLAlchemy inspector (works with PostgreSQL and SQLite).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text, inspect


def migrate():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            existing = [c['name'] for c in insp.get_columns('break_requests')]
            if 'responded_at' not in existing:
                db.session.execute(text("ALTER TABLE break_requests ADD COLUMN responded_at TIMESTAMP"))
                db.session.commit()
                print("[OK] Added responded_at to break_requests")
            else:
                print("[OK] responded_at already exists")
            if 'response_message' not in existing:
                db.session.execute(text("ALTER TABLE break_requests ADD COLUMN response_message TEXT"))
                db.session.commit()
                print("[OK] Added response_message to break_requests")
            else:
                print("[OK] response_message already exists")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] {e}")
            raise


if __name__ == '__main__':
    migrate()
