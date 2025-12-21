"""
Simple test script to check login functionality
Run this while the backend server is running
"""

import requests
import json

def test_login():
    url = "http://localhost:5000/api/login"
    
    # Test with demo credentials
    data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        print("Testing login...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, json=data, timeout=5)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Login successful!")
            return True
        else:
            print(f"\n❌ Login failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("Make sure the backend server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    test_login()

