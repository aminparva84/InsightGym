"""
Standalone script to create demo user
Run this directly: python create_demo_user_standalone.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up minimal Flask app context
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import sqlite3

# Create minimal app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///raha_fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define minimal User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='fa')

def create_demo_user():
    """Create demo user"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if demo user already exists
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

