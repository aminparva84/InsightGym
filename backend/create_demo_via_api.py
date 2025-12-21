"""
Create demo user via API registration endpoint
This avoids model conflicts and ensures correct password hashing
"""

import requests
import json

def create_demo_user():
    url = "http://localhost:5000/api/register"
    
    data = {
        "username": "demo",
        "email": "demo@raha-fitness.com",
        "password": "demo123",
        "language": "fa"
    }
    
    try:
        print("Attempting to register demo user via API...")
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 201:
            result = response.json()
            print("\n" + "="*50)
            print("SUCCESS: DEMO USER CREATED!")
            print("="*50)
            print("Username: demo")
            print("Password: demo123")
            print("Email: demo@raha-fitness.com")
            print("\nYou can now log in!")
            print("="*50)
            return True
        elif response.status_code == 400:
            result = response.json()
            error = result.get('error', '')
            if 'already exists' in error.lower():
                print("\n" + "="*50)
                print("INFO: DEMO USER ALREADY EXISTS")
                print("="*50)
                print("The user exists but login is failing.")
                print("\nThe password hash may be incorrect.")
                print("Please delete the existing user from the database")
                print("or register with a different username via the UI.")
                print("="*50)
                return False
            else:
                print(f"Error: {error}")
                return False
        else:
            print(f"Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server.")
        print("\nPlease make sure the backend is running:")
        print("  cd backend")
        print("  python app.py")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    create_demo_user()
