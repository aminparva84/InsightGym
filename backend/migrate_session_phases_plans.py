"""
Migration: add session_phases_json and training_plans_products_json to site_settings.
Run once: python migrate_session_phases_plans.py
"""

from app import app, db
from sqlalchemy import text, inspect


def migrate():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            table_name = "site_settings"
            existing_columns = [c["name"] for c in insp.get_columns(table_name)]

            for col_name in ("session_phases_json", "training_plans_products_json"):
                if col_name not in existing_columns:
                    db.session.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} TEXT")
                    )
                    print(f"[OK] Added {col_name}")
                else:
                    print(f"[OK] {col_name} already exists")
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
