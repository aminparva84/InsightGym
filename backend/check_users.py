"""
Check existing users in the database and diagnose login issues
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import check_password_hash

def check_users():
    with app.app_context():
        try:
            users = User.query.all()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            print("  Ensure DATABASE_URL is set (e.g. postgresql://...) and the database exists.")
            return
        
        print("[OK] Connected to database")
        
        print(f"\n{'='*60}")
        print(f"Total users in database: {len(users)}")
        print(f"{'='*60}\n")
        
        if len(users) == 0:
            print("[WARNING] No users found in the database!")
            print("\nTo create a demo user, run:")
            print("  python recreate_demo_user.py")
            print("\nOr register a new user through the web interface.")
            return
        
        # List all users
        for i, user in enumerate(users, 1):
            print(f"User #{i}:")
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Language: {user.language}")
            print(f"  Created: {user.created_at}")
            print(f"  Password Hash: {user.password_hash[:50]}...")
            
            # Test password verification
            test_passwords = ['demo123', 'password', '123456', user.username]
            print(f"  Testing passwords:")
            for test_pwd in test_passwords:
                try:
                    match = check_password_hash(user.password_hash, test_pwd)
                    status = "[MATCH]" if match else "[no match]"
                    print(f"    '{test_pwd}': {status}")
                except Exception as e:
                    print(f"    '{test_pwd}': ERROR - {e}")
            print()

if __name__ == '__main__':
    check_users()

