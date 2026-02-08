"""
Migration: add voice_url, trainer_notes_fa, trainer_notes_en to exercises table
for training movement info (video/voice/text) in admin and member training plan.

Run once: python migrate_exercise_movement_info.py
"""

from app import app, db
from sqlalchemy import text, inspect


def migrate():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            table_name = "exercises"
            existing_columns = [c["name"] for c in insp.get_columns(table_name)]

            # Use TEXT for SQLite; PostgreSQL accepts TEXT for all
            to_add = [
                ("voice_url", "TEXT"),
                ("trainer_notes_fa", "TEXT"),
                ("trainer_notes_en", "TEXT"),
            ]
            for col_name, col_type in to_add:
                if col_name not in existing_columns:
                    db.session.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    )
                    print(f"[OK] Added {col_name}")
                else:
                    print(f"[OK] {col_name} already exists")
            db.session.commit()
            print("[OK] Exercise movement info columns ready.")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
