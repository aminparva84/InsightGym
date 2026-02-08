"""
Migration: add ask_post_set_questions to exercises table.
Run: python migrate_ask_post_set_questions.py
"""

from app import app, db
from sqlalchemy import text, inspect

def run():
    with app.app_context():
        insp = inspect(db.engine)
        cols = [c['name'] for c in insp.get_columns('exercises')]
        if 'ask_post_set_questions' in cols:
            print("Column ask_post_set_questions already exists. Skipping.")
            return
        try:
            if db.engine.url.get_dialect().name == 'sqlite':
                db.session.execute(text(
                    "ALTER TABLE exercises ADD COLUMN ask_post_set_questions BOOLEAN DEFAULT 0"
                ))
            else:
                db.session.execute(text("""
                    ALTER TABLE exercises
                    ADD COLUMN ask_post_set_questions BOOLEAN NOT NULL DEFAULT FALSE
                """))
            db.session.commit()
            print("Migration done: ask_post_set_questions added to exercises.")
        except Exception as e:
            db.session.rollback()
            raise

if __name__ == "__main__":
    run()
