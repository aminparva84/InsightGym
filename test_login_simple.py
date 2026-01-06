"""Simple login test for testuser_complete"""
import requests
import sys

BASE_URL = "http://localhost:5000"
credentials = {"username": "testuser_complete", "password": "Test123456!"}

print("Testing login with testuser_complete...")
print(f"Username: {credentials['username']}")
print(f"Password: {credentials['password'][:3]}***")

response = requests.post(f"{BASE_URL}/api/login", json=credentials)
print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    user = data.get('user', {})
    print("SUCCESS: Login successful!")
    print(f"Username: {user.get('username')}")
    print(f"User ID: {user.get('id')}")
    print(f"Email: {user.get('email')}")
    print(f"Token (first 50 chars): {token[:50]}...")
    
    # Test /api/user endpoint
    print("\n--- Testing /api/user endpoint ---")
    user_resp = requests.get(f"{BASE_URL}/api/user", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {user_resp.status_code}")
    if user_resp.status_code == 200:
        user_data = user_resp.json()
        print("SUCCESS: /api/user works!")
        print(f"User: {user_data.get('username')}, Email: {user_data.get('email')}")
    else:
        print(f"FAILED: {user_resp.text}")
    
    # Test /api/user/profile endpoint
    print("\n--- Testing /api/user/profile endpoint ---")
    profile_resp = requests.get(f"{BASE_URL}/api/user/profile", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {profile_resp.status_code}")
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        print("SUCCESS: /api/user/profile works!")
        print(f"Age: {profile.get('age')}")
        print(f"Weight: {profile.get('weight')}")
        print(f"Height: {profile.get('height')}")
        print(f"Gender: {profile.get('gender')}")
        print(f"Training Level: {profile.get('training_level')}")
    elif profile_resp.status_code == 404:
        print("INFO: Profile not found (user hasn't created profile yet)")
    else:
        print(f"FAILED: {profile_resp.text}")
    
    print("\n=== ALL TESTS COMPLETE ===")
    sys.exit(0)
else:
    print(f"FAILED: Login failed")
    print(f"Response: {response.text}")
    sys.exit(1)
