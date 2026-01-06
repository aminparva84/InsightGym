"""
Reset passwords for all users in the database
"""

import sqlite3
import os
import sys
import codecs
from werkzeug.security import generate_password_hash

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def reset_all_passwords():
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
        
        # Get all users
        cursor.execute("SELECT id, username, email FROM user")
        users = cursor.fetchall()
        
        if not users:
            print("[INFO] No users found in database")
            conn.close()
            return False
        
        print("="*60)
        print("Resetting passwords for all users...")
        print("="*60)
        print()
        
        for user_id, username, email in users:
            # Use username as password for simplicity, or use a default
            new_password = 'demo123'  # You can change this to username if preferred
            password_hash = generate_password_hash(new_password)
            
            cursor.execute(
                "UPDATE user SET password_hash = ? WHERE id = ?",
                (password_hash, user_id)
            )
            
            print(f"User: {username}")
            print(f"  Email: {email}")
            print(f"  New Password: {new_password}")
            print()
        
        conn.commit()
        conn.close()
        
        print("="*60)
        print("All passwords reset successfully!")
        print("="*60)
        print("\nAll users can now login with password: demo123")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = reset_all_passwords()
    sys.exit(0 if success else 1)

