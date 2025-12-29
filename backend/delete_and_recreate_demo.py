"""
Delete existing demo user and recreate via API
"""

import requests
import sqlite3
import os

# First, try to delete via SQLite directly
db_path = os.path.join(os.path.dirname(__file__), 'raha_fitness.db')

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete demo user
        cursor.execute("DELETE FROM user WHERE username = 'demo'")
        conn.commit()
        conn.close()
        print("Deleted existing demo user from database")
    except Exception as e:
        print(f"Could not delete via SQLite: {e}")

# Now try to register via API
url = "http://localhost:5000/api/register"

data = {
    "username": "demo",
    "email": "demo@raha-fitness.com",
    "password": "demo123",
    "language": "fa"
}

try:
    print("Registering demo user via API...")
    response = requests.post(url, json=data, timeout=5)
    
    if response.status_code == 201:
        print("\n" + "="*50)
        print("SUCCESS: DEMO USER CREATED!")
        print("="*50)
        print("Username: demo")
        print("Password: demo123")
        print("Email: demo@raha-fitness.com")
        print("\nYou can now log in!")
        print("="*50)
    else:
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {result}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Backend not running. Please start it first:")
    print("  cd backend")
    print("  python app.py")
except Exception as e:
    print(f"Error: {e}")



