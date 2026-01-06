"""
Initialize database and create demo user
This script will:
1. Create the database if it doesn't exist
2. Create all tables
3. Create a demo user with known credentials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def init_database():
    with app.app_context():
        print("="*60)
        print("Initializing Database...")
        print("="*60)
        
        # Create all tables (ignore errors if they already exist)
        print("\n[1/3] Creating database tables...")
        try:
            db.create_all()
            print("[OK] Database tables created/verified")
        except Exception as e:
            # Tables might already exist, that's okay
            if "already exists" in str(e):
                print("[INFO] Database tables already exist (this is normal)")
            else:
                print(f"[WARNING] Error creating tables: {e}")
                print("[INFO] Continuing anyway...")
        
        # Check if demo user exists
        print("\n[2/3] Checking for existing demo user...")
        existing_user = User.query.filter_by(username='demo').first()
        
        if existing_user:
            print(f"[INFO] Demo user already exists: {existing_user.username}")
            print("[INFO] Resetting password to 'demo123'...")
            existing_user.password_hash = generate_password_hash('demo123')
            db.session.commit()
            print("[OK] Password reset complete")
        else:
            print("[INFO] Creating new demo user...")
            demo_user = User(
                username='demo',
                email='demo@raha-fitness.com',
                password_hash=generate_password_hash('demo123'),
                language='fa',
                created_at=datetime.utcnow()
            )
            db.session.add(demo_user)
            db.session.commit()
            print("[OK] Demo user created")
        
        # Verify the user
        print("\n[3/3] Verifying demo user...")
        created = User.query.filter_by(username='demo').first()
        if created:
            password_check = check_password_hash(created.password_hash, 'demo123')
            if password_check:
                print("[OK] Password verification: PASSED")
            else:
                print("[ERROR] Password verification: FAILED")
                return False
            
            print("\n" + "="*60)
            print("DATABASE INITIALIZED SUCCESSFULLY!")
            print("="*60)
            print("\nDemo User Credentials:")
            print(f"  Username: {created.username}")
            print(f"  Email: {created.email}")
            print(f"  Password: demo123")
            print(f"  Language: {created.language}")
            print("\nYou can now login with these credentials!")
            print("="*60)
            return True
        else:
            print("[ERROR] Failed to create/verify demo user")
            return False

if __name__ == '__main__':
    try:
        success = init_database()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

