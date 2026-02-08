"""
Create a test member with 7-day trial and NO training plan.
Use this account to test the trial flow: login, open Training Program tab,
and the AI will generate a 1-week trial program.

Run: python create_trial_test_member.py
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


USERNAME = "trial_test"
EMAIL = "trial_test@test.com"
PASSWORD = "trial123"


def run():
    with app.app_context():
        from models import (
            TrainingProgram,
            MemberWeeklyGoal,
            MemberTrainingActionCompletion,
            TrainingActionNote,
        )

        existing = User.query.filter_by(username=USERNAME).first()
        if existing:
            # Reset password so login always works (fixes hash/DB mismatch)
            existing.password_hash = generate_password_hash(PASSWORD)
            # Remove any user-specific training programs (and dependents) so trial can generate a fresh one
            program_ids = [p.id for p in db.session.query(TrainingProgram).filter_by(user_id=existing.id).all()]
            deleted = 0
            for pid in program_ids:
                db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
                db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
                db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
                db.session.query(TrainingProgram).filter_by(id=pid).delete()
                deleted += 1
            if existing.trial_ends_at is None or existing.trial_ends_at < datetime.utcnow():
                existing.trial_ends_at = datetime.utcnow() + timedelta(days=7)
            db.session.commit()
            print("\n" + "=" * 60)
            print("TRIAL TEST MEMBER ALREADY EXISTS (password & trial reset)")
            print("=" * 60)
            print(f"  Username: {USERNAME}")
            print(f"  Password: {PASSWORD}")
            print(f"  Email:    {EMAIL}")
            print(f"  Removed {deleted} existing training program(s). Trial ends: {existing.trial_ends_at}")
            print("\n  Log in with the credentials above, then open 'Training Program' tab.")
            print("=" * 60 + "\n")
            return

        user = User(
            username=USERNAME,
            email=EMAIL,
            password_hash=generate_password_hash(PASSWORD),
            language="fa",
            role="member",
            trial_ends_at=datetime.utcnow() + timedelta(days=7),
        )
        db.session.add(user)
        db.session.commit()

        print("\n" + "=" * 60)
        print("TRIAL TEST MEMBER CREATED")
        print("=" * 60)
        print(f"  Username: {USERNAME}")
        print(f"  Password: {PASSWORD}")
        print(f"  Email:    {EMAIL}")
        print(f"  Trial ends: {user.trial_ends_at}")
        print("\n  This member has NO training plan. When they open the")
        print("  'Training Program' tab, the AI will create a 1-week trial program.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    run()
