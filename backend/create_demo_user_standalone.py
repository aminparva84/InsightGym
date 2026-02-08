"""
Standalone script to create demo user.
Run this directly: python create_demo_user_standalone.py
Uses main app and DATABASE_URL (PostgreSQL). Set DATABASE_URL in .env (see .env.example).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_user():
    """Create demo user"""
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            print("Set DATABASE_URL (e.g. postgresql://user:password@localhost:5432/raha_fitness)")
            return
        demo_user = User.query.filter_by(username='demo').first()
        if demo_user:
            print("\n" + "="*50)
            print("DEMO USER ALREADY EXISTS!")
            print("="*50)
            print(f"Username: demo")
            print(f"Password: demo123")
            print(f"Email: demo@raha-fitness.com")
            print("="*50)
            return
        
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@raha-fitness.com',
            password_hash=generate_password_hash('demo123'),
            language='fa',
            created_at=datetime.utcnow()
        )
        db.session.add(demo_user)
        db.session.commit()
        
        print("\n" + "="*50)
        print("DEMO USER CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Username: demo")
        print(f"Password: demo123")
        print(f"Email: demo@raha-fitness.com")
        print(f"Language: Farsi (Persian)")
        print("\nYou can now log in to see the member landing page!")
        print("="*50)

if __name__ == '__main__':
    create_demo_user()

