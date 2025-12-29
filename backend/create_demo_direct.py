"""
Create demo user directly using app context
This script uses the actual app.py User model
"""

# Run this with: python -m flask shell
# Or: python -c "exec(open('create_demo_direct.py').read())"

from app import app, db
from werkzeug.security import generate_password_hash

with app.app_context():
    # Import User after app context
    from app import User
    from datetime import datetime
    
    # Check if exists
    existing = User.query.filter_by(username='demo').first()
    if existing:
        print("Demo user already exists! Deleting and recreating...")
        db.session.delete(existing)
        db.session.commit()
    
    # Create new user
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
    print("DEMO USER CREATED!")
    print("="*50)
    print("Username: demo")
    print("Password: demo123")
    print("="*50)



