"""
Assign exactly one training plan to each member user.

Behavior:
- Keeps only one general program (the first by id); removes extra general programs and their dependents.
- For each member:
  - If they already have multiple user-specific programs, keeps the first and deletes the rest (+ dependents).
  - If they have none, copies the single general program to them.

Run: python assign_training_plan_to_members.py
"""

from app import app, db
from app import User
from models import TrainingProgram, MemberWeeklyGoal, MemberTrainingActionCompletion, TrainingActionNote
import json


def run():
    with app.app_context():
        # General programs (user_id is NULL) - keep only one
        general = (
            db.session.query(TrainingProgram)
            .filter(TrainingProgram.user_id.is_(None))
            .order_by(TrainingProgram.id)
            .all()
        )
        if not general:
            print("No general training programs found. Run create_training_programs.py first.")
            return

        keep_general = general[0]
        extra_general = general[1:]
        if extra_general:
            for prog in extra_general:
                pid = prog.id
                db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
                db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
                db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
                db.session.delete(prog)
            db.session.commit()
            print(f"Removed {len(extra_general)} extra general program(s). Keeping id={keep_general.id}.")

        # All members (role = 'member')
        members = db.session.query(User).filter(User.role == 'member').all()
        if not members:
            print("No member users found.")
            return

        assigned = 0
        cleaned = 0
        for user in members:
            user_programs = (
                db.session.query(TrainingProgram)
                .filter_by(user_id=user.id)
                .order_by(TrainingProgram.id)
                .all()
            )
            if user_programs:
                # Keep the first, delete the rest
                keep = user_programs[0]
                for prog in user_programs[1:]:
                    pid = prog.id
                    db.session.query(MemberWeeklyGoal).filter_by(training_program_id=pid).delete()
                    db.session.query(MemberTrainingActionCompletion).filter_by(training_program_id=pid).delete()
                    db.session.query(TrainingActionNote).filter_by(training_program_id=pid).delete()
                    db.session.delete(prog)
                    cleaned += 1
                continue
            # Copy single general program for this member
            template = keep_general
            copy_program = TrainingProgram(
                user_id=user.id,
                name_fa=template.name_fa,
                name_en=template.name_en,
                description_fa=template.description_fa,
                description_en=template.description_en,
                duration_weeks=template.duration_weeks,
                training_level=template.training_level,
                category=template.category,
                sessions=template.sessions,
            )
            db.session.add(copy_program)
            assigned += 1
            print(f"Assigned program to {user.username} (id={user.id})")

        db.session.commit()
        print(f"\nDone. Assigned training plan to {assigned} member(s).")
        if cleaned:
            print(f"Removed {cleaned} extra member program(s).")


if __name__ == "__main__":
    run()
