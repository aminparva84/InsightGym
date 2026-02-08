"""
Migration: add ai_settings_json to site_settings.
Run: python migrate_ai_settings.py
"""

from app import app, db
from sqlalchemy import text, inspect

def run():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            cols = [c['name'] for c in insp.get_columns('site_settings')]
            if 'ai_settings_json' in cols:
                print("Column ai_settings_json already exists. Skipping.")
                return
            if db.engine.url.get_dialect().name == 'sqlite':
                db.session.execute(text(
                    "ALTER TABLE site_settings ADD COLUMN ai_settings_json TEXT"
                ))
            else:
                db.session.execute(text(
                    "ALTER TABLE site_settings ADD COLUMN ai_settings_json TEXT"
                ))
            db.session.commit()
            print("Migration done: ai_settings_json added to site_settings.")
        except Exception as e:
            db.session.rollback()
            raise

if __name__ == "__main__":
    run()
