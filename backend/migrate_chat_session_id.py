"""
Migration script to add session_id column to chat_history for conversation grouping.
Run once to support conversation-based chat history.

Usage (from backend folder):
  python migrate_chat_session_id.py
"""

from sqlalchemy import text
from app import app, db


def migrate():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text(
                    'ALTER TABLE chat_history ADD COLUMN session_id VARCHAR(36)'
                ))
                conn.commit()
            print("[OK] Added session_id to chat_history.")
        except Exception as e:
            err = str(e).lower()
            if 'already exists' in err or 'duplicate' in err or 'column' in err:
                print("[OK] session_id column already present.")
            else:
                print(f"[ERROR] {e}")
                raise


if __name__ == "__main__":
    migrate()
