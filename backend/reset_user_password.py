"""
Reset password for any user in the database.
Usage: python reset_user_password.py <username> [new_password]
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from app import app, db, User

def reset_password(username, new_password='demo123'):
    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            return False
        if not user:
            print(f"[ERROR] User '{username}' not found in database")
            return False
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print("="*60)
        print("PASSWORD RESET SUCCESSFUL!")
        print("="*60)
        print(f"Username: {username}")
        print(f"Email: {user.email}")
        print(f"New Password: {new_password}")
        print("="*60)
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reset_user_password.py <username> [new_password]")
        print("Example: python reset_user_password.py demo demo123")
        sys.exit(1)
    username = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) > 2 else 'demo123'
    success = reset_password(username, new_password)
    sys.exit(0 if success else 1)



