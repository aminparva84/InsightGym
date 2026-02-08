"""
Delete existing demo user and recreate (via SQLAlchemy, then optionally via API).
Uses Flask app context and SQLAlchemy (works with PostgreSQL or SQLite via DATABASE_URL).
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

# Delete demo user via SQLAlchemy
with app.app_context():
    try:
        demo = User.query.filter_by(username='demo').first()
        if demo:
            db.session.delete(demo)
            db.session.commit()
            print("Deleted existing demo user from database")
    except Exception as e:
        print(f"Could not delete demo user: {e}")

# Try to register via API (backend must be running)
url = "http://localhost:5000/api/register"
data = {
    "username": "demo",
    "email": "demo@raha-fitness.com",
    "password": "demo123",
    "language": "fa"
}

try:
    print("Registering demo user via API...")
    response = requests.post(url, json=data, timeout=5)
    if response.status_code == 201:
        print("\n" + "="*50)
        print("SUCCESS: DEMO USER CREATED!")
        print("="*50)
        print("Username: demo")
        print("Password: demo123")
        print("Email: demo@raha-fitness.com")
        print("\nYou can now log in!")
        print("="*50)
    else:
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {result}")
        # Fallback: create demo user directly via SQLAlchemy
        with app.app_context():
            if not User.query.filter_by(username='demo').first():
                demo_user = User(
                    username='demo',
                    email='demo@raha-fitness.com',
                    password_hash=generate_password_hash('demo123'),
                    language='fa',
                    created_at=datetime.utcnow()
                )
                db.session.add(demo_user)
                db.session.commit()
                print("\nDemo user created directly in database (API was unavailable or rejected).")
except requests.exceptions.ConnectionError:
    # Backend not running: create demo user directly
    with app.app_context():
        try:
            if not User.query.filter_by(username='demo').first():
                demo_user = User(
                    username='demo',
                    email='demo@raha-fitness.com',
                    password_hash=generate_password_hash('demo123'),
                    language='fa',
                    created_at=datetime.utcnow()
                )
                db.session.add(demo_user)
                db.session.commit()
                print("\nDemo user created directly (backend was not running).")
                print("Username: demo, Password: demo123")
        except Exception as e:
            print(f"ERROR: Backend not running and could not create user: {e}")
            print("  Start backend first: cd backend && python app.py")
except Exception as e:
    print(f"Error: {e}")
