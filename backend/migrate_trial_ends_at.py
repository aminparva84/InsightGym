"""
Migration: add trial_ends_at to user table (7-day free trial).
Run: python migrate_trial_ends_at.py
"""

from app import app, db
from sqlalchemy import text, inspect


def run():
    with app.app_context():
        try:
            insp = inspect(db.engine)
            cols = [c["name"] for c in insp.get_columns("user")]
            if "trial_ends_at" in cols:
                print("Column trial_ends_at already exists. Skipping.")
                return
            db.session.execute(text(
                "ALTER TABLE \"user\" ADD COLUMN trial_ends_at TIMESTAMP"
            ))
            db.session.commit()
            print("Migration done: trial_ends_at added to user.")
        except Exception as e:
            db.session.rollback()
            raise


if __name__ == "__main__":
    run()
