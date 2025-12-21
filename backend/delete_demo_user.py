"""
Delete demo user from database
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'raha_fitness.db')

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    # Try to find and delete demo user
    table_name = 'user'  # Default table name
    
    # Check if user exists
    cursor.execute(f"SELECT username FROM {table_name} WHERE username='demo'")
    user = cursor.fetchone()
    
    if user:
        print(f"Found demo user in table '{table_name}'")
        cursor.execute(f"DELETE FROM {table_name} WHERE username='demo'")
        conn.commit()
        print("Demo user deleted successfully!")
    else:
        print("Demo user not found in database")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

