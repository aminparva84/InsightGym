"""
Reset demo user password via API
"""

import requests

url = "http://localhost:5000/api/reset-demo-password"

data = {
    "password": "demo123"
}

try:
    print("Resetting demo user password...")
    response = requests.post(url, json=data, timeout=5)
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*50)
        print("SUCCESS: DEMO USER PASSWORD RESET!")
        print("="*50)
        print(f"Username: {result['username']}")
        print(f"Password: {result['password']}")
        print("\nYou can now log in!")
        print("="*50)
    else:
        result = response.json()
        print(f"Error: {result.get('error', 'Unknown error')}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Backend not running. Please start it first:")
    print("  cd backend")
    print("  python app.py")
except Exception as e:
    print(f"Error: {e}")

