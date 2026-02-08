"""
Delete demo user from database.
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def delete_demo_user():
    with app.app_context():
        try:
            user = User.query.filter_by(username='demo').first()
        except Exception as e:
            print(f"[ERROR] Could not connect to database: {e}")
            return False
        if user:
            db.session.delete(user)
            db.session.commit()
            print("Demo user deleted successfully!")
        else:
            print("Demo user not found in database")
        return True

if __name__ == '__main__':
    delete_demo_user()
