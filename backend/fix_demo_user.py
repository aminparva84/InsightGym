"""
Fix demo user - Delete and recreate using the actual app models
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual app
from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import User from app (the actual model)
# We need to do this carefully to avoid model conflicts
with app.app_context():
    # Get the User model from the app's db.Model registry
    User = db.Model._decl_class_registry.get('User')
    
    if not User:
        # Fallback: try to get it from app module
        from app import User
    
    # Delete existing demo user if exists
    existing = User.query.filter_by(username='demo').first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print("Deleted existing demo user")
    
    # Create new demo user
    demo_user = User(
        username='demo',
        email='demo@raha-fitness.com',
        password_hash=generate_password_hash('demo123'),
        language='fa',
        created_at=datetime.utcnow()
    )
    
    db.session.add(demo_user)
    db.session.commit()
    
    # Verify the user was created and password works
    created = User.query.filter_by(username='demo').first()
    if created and check_password_hash(created.password_hash, 'demo123'):
        print("\n" + "="*50)
        print("DEMO USER CREATED AND VERIFIED!")
        print("="*50)
        print(f"Username: demo")
        print(f"Password: demo123")
        print(f"Email: demo@raha-fitness.com")
        print(f"Password verification: PASSED")
        print("="*50)
    else:
        print("ERROR: User created but password verification failed!")



