"""
Create admin user account
Run this script to create an admin user with full access
"""

from app import app, db
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Create admin user"""
    with app.app_context():
        # Import User model
        from app import User
        
        # Check if admin already exists
        existing_admin = db.session.query(User).filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Email: {existing_admin.email}")
            print(f"Role: {existing_admin.role if hasattr(existing_admin, 'role') else 'N/A'}")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@insightgym.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            language='fa',
            created_at=datetime.utcnow()
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("ADMIN USER CREATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@insightgym.com")
        print(f"Role: admin")
        print("=" * 70)
        print("\nPlease change the password after first login!")
        print("=" * 70 + "\n")
        
        return admin_user

if __name__ == '__main__':
    create_admin_user()

