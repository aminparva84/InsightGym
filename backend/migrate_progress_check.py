"""
Migration: create progress_check_requests table.
Run once: python migrate_progress_check.py
"""

from app import app, db
from models import ProgressCheckRequest


def migrate():
    with app.app_context():
        try:
            ProgressCheckRequest.__table__.create(db.engine, checkfirst=True)
            print("[OK] progress_check_requests table ready")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
