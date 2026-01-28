"""
Migration: Add tables for member features (weekly goals, daily steps, break requests).
Run with: python migrate_member_features.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db


def migrate():
    with app.app_context():
        # Create only the new tables - SQLAlchemy create_all creates missing tables only
        from models import MemberWeeklyGoal, DailySteps, BreakRequest
        db.create_all()
        print("[OK] member_weekly_goals, daily_steps, break_requests tables created/verified")


if __name__ == '__main__':
    migrate()
