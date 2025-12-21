"""
Recreate demo user using the exact same method as registration endpoint
This ensures password hash matches
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

with app.app_context():
    # Import User from app
    from app import User
    
    # Delete existing demo user
    existing = User.query.filter_by(username='demo').first()
    if existing:
        print("Deleting existing demo user...")
        db.session.delete(existing)
        db.session.commit()
    
    # Create user EXACTLY as registration endpoint does
    demo_user = User(
        username='demo',
        email='demo@raha-fitness.com',
        password_hash=generate_password_hash('demo123'),  # Same method as registration
        language='fa'
    )
    
    db.session.add(demo_user)
    db.session.commit()
    
    # Verify password works
    created = User.query.filter_by(username='demo').first()
    if created:
        password_check = check_password_hash(created.password_hash, 'demo123')
        print("\n" + "="*50)
        print("DEMO USER RECREATED!")
        print("="*50)
        print(f"Username: {created.username}")
        print(f"Email: {created.email}")
        print(f"Password Hash: {created.password_hash[:50]}...")
        print(f"Password Verification: {'✓ PASSED' if password_check else '✗ FAILED'}")
        print("="*50)
        
        if password_check:
            print("\n✅ Login should work now!")
            print("Username: demo")
            print("Password: demo123")
        else:
            print("\n❌ Password verification failed. There may be an issue.")
    else:
        print("❌ Failed to create user!")

