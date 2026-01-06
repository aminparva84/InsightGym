"""
Reset password for any user in the database
Usage: python reset_user_password.py <username> [new_password]
"""

import sqlite3
import sys
import os
from werkzeug.security import generate_password_hash

def reset_password(username, new_password='demo123'):
    db_paths = [
        'instance/raha_fitness.db',
        'raha_fitness.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("[ERROR] Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, username, email FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"[ERROR] User '{username}' not found in database")
            conn.close()
            return False
        
        # Reset password
        password_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE user SET password_hash = ? WHERE username = ?",
            (password_hash, username)
        )
        conn.commit()
        conn.close()
        
        print("="*60)
        print("PASSWORD RESET SUCCESSFUL!")
        print("="*60)
        print(f"Username: {username}")
        print(f"Email: {user[2]}")
        print(f"New Password: {new_password}")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reset_user_password.py <username> [new_password]")
        print("Example: python reset_user_password.py demo demo123")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) > 2 else 'demo123'
    
    success = reset_password(username, new_password)
    sys.exit(0 if success else 1)



