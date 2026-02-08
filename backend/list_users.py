"""
List all users in the database.
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from app import app, User

def list_users():
    with app.app_context():
        try:
            users = User.query.all()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            return
        print("="*60)
        print(f"Total users in database: {len(users)}")
        print("="*60)
        if len(users) == 0:
            print("\nNo users found in the database.")
            print("\nTo create a demo user, run:")
            print("  python init_database.py")
        else:
            print()
            for user in users:
                print(f"User ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Language: {user.language}")
                print(f"  Created: {user.created_at}")
                print()

if __name__ == '__main__':
    list_users()

