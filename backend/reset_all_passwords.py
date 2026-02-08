"""
Reset passwords for all users in the database.
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import os
import sys
import codecs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from werkzeug.security import generate_password_hash
from app import app, db, User

def reset_all_passwords():
    with app.app_context():
        try:
            users = User.query.all()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            return False
        if not users:
            print("[INFO] No users found in database")
            return False
        print("="*60)
        print("Resetting passwords for all users...")
        print("="*60)
        print()
        new_password = 'demo123'
        for user in users:
            user.password_hash = generate_password_hash(new_password)
            print(f"User: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  New Password: {new_password}")
            print()
        db.session.commit()
        print("="*60)
        print("All passwords reset successfully!")
        print("="*60)
        print("\nAll users can now login with password: demo123")
        print("="*60)
        return True

if __name__ == '__main__':
    success = reset_all_passwords()
    sys.exit(0 if success else 1)

