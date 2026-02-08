"""
Simple script to fix login issues by creating/resetting demo user.
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_login():
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[ERROR] Could not create/connect to database: {e}")
            print("[INFO] Ensure DATABASE_URL is set (e.g. postgresql://...) and the database exists.")
            return False
        existing = User.query.filter_by(username='demo').first()
        if existing:
            print("[INFO] Found existing demo user, resetting password to 'demo123'...")
            existing.password_hash = generate_password_hash('demo123')
            db.session.commit()
            print("[OK] Password reset complete")
        else:
            print("[INFO] Creating new demo user...")
            demo_user = User(
                username='demo',
                email='demo@raha-fitness.com',
                password_hash=generate_password_hash('demo123'),
                language='fa',
                created_at=datetime.utcnow()
            )
            db.session.add(demo_user)
            db.session.commit()
            print("[OK] Demo user created")
        user = User.query.filter_by(username='demo').first()
        if user:
            print("\n" + "="*60)
            print("LOGIN FIXED!")
            print("="*60)
            print("\nDemo User Credentials:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Password: demo123")
            print("\nYou can now login with these credentials!")
            print("="*60)
            return True
        print("[ERROR] Failed to create/verify user")
        return False

if __name__ == '__main__':
    success = fix_login()
    sys.exit(0 if success else 1)
