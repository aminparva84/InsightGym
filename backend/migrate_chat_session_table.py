"""
Migration script to create the chat_session table for conversation titles.
Run once to support renaming conversations.

Usage (from backend folder):
  python migrate_chat_session_table.py
"""

from app import app, db
from app import ChatSession


def migrate():
    with app.app_context():
        try:
            db.create_all()
            # ChatSession is defined in app.py; create_all will create chat_session if missing
            print("[OK] chat_session table is ready.")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
