"""
Migration: create member_training_action_completions, notifications, training_action_notes.
Run once: python migrate_training_progress_notifications.py
"""

from app import app, db
from models import MemberTrainingActionCompletion, Notification, TrainingActionNote


def migrate():
    with app.app_context():
        try:
            db.create_all()
            print("[OK] member_training_action_completions, notifications, training_action_notes tables ready.")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
