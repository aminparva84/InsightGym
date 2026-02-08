"""
Migration: add note_notify_at_seconds to exercises table.
Admin can set at what time (seconds from start) during an exercise the note/voice should be notified to the member.

Run once: python migrate_note_notify_at.py
"""

from app import app, db
from sqlalchemy import text, inspect


def migrate():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            table_name = "exercises"
            existing_columns = [c["name"] for c in insp.get_columns(table_name)]

            if "note_notify_at_seconds" not in existing_columns:
                db.session.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN note_notify_at_seconds INTEGER")
                )
                print("[OK] Added note_notify_at_seconds")
            else:
                print("[OK] note_notify_at_seconds already exists")
            db.session.commit()
            print("[OK] Migration done.")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
