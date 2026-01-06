"""
Simple script to fix login issues by creating/resetting demo user
Uses direct SQL to avoid model conflicts
"""

import sqlite3
import sys
import os
from werkzeug.security import generate_password_hash

def fix_login():
    # Check both possible locations
    db_paths = [
        'instance/raha_fitness.db',  # Flask instance folder
        'raha_fitness.db'  # Root backend folder
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"[ERROR] Database file not found in any of these locations:")
        for path in db_paths:
            print(f"  - {path}")
        print("\n[INFO] The database will be created when you start the backend server.")
        print("[INFO] After starting the server, run this script again or register a new user.")
        return False
    
    print(f"[INFO] Found database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("[ERROR] User table not found in database")
            print("[INFO] Please start the backend server first to create the database tables")
            conn.close()
            return False
        
        # Check for existing demo user
        cursor.execute("SELECT id, username, email FROM user WHERE username = ?", ('demo',))
        existing = cursor.fetchone()
        
        password_hash = generate_password_hash('demo123')
        
        if existing:
            print(f"[INFO] Found existing user: {existing[1]}")
            print("[INFO] Resetting password to 'demo123'...")
            cursor.execute(
                "UPDATE user SET password_hash = ? WHERE username = ?",
                (password_hash, 'demo')
            )
            conn.commit()
            print("[OK] Password reset complete")
        else:
            print("[INFO] Creating new demo user...")
            cursor.execute(
                """INSERT INTO user (username, email, password_hash, language, created_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                ('demo', 'demo@raha-fitness.com', password_hash, 'fa')
            )
            conn.commit()
            print("[OK] Demo user created")
        
        # Verify
        cursor.execute("SELECT username, email FROM user WHERE username = ?", ('demo',))
        user = cursor.fetchone()
        
        if user:
            print("\n" + "="*60)
            print("LOGIN FIXED!")
            print("="*60)
            print("\nDemo User Credentials:")
            print(f"  Username: {user[0]}")
            print(f"  Email: {user[1]}")
            print(f"  Password: demo123")
            print("\nYou can now login with these credentials!")
            print("="*60)
            conn.close()
            return True
        else:
            print("[ERROR] Failed to create/verify user")
            conn.close()
            return False
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_login()
    sys.exit(0 if success else 1)

