"""
Create demo user for testing - Simple version
Run this script to create a demo user
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_user():
    """Create demo user"""
    
    with app.app_context():
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

