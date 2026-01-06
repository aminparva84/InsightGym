"""
List all users in the database using direct SQL
"""

import sqlite3
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def list_users():
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
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, language, created_at FROM user")
        users = cursor.fetchall()
        
        print("="*60)
        print(f"Total users in database: {len(users)}")
        print("="*60)
        
        if len(users) == 0:
            print("\nNo users found in the database.")
            print("\nTo create a demo user, run:")
            print("  python fix_login.py")
        else:
            print()
            for user in users:
                print(f"User ID: {user[0]}")
                print(f"  Username: {user[1]}")
                print(f"  Email: {user[2]}")
                print(f"  Language: {user[3]}")
                print(f"  Created: {user[4]}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    list_users()

