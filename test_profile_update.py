"""Test profile update functionality"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Login
print("=== LOGGING IN ===")
login_resp = requests.post(f"{BASE_URL}/api/login", json={
    "username": "testuser_complete",
    "password": "Test123456!"
})
print(f"Login Status: {login_resp.status_code}")

if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    exit(1)

token = login_resp.json()['access_token']
print("Token received")

# Update profile
print("\n=== UPDATING PROFILE ===")
update_data = {
    "age": 30,
    "weight": 80,
    "height": 180,
    "gender": "male",
    "training_level": "intermediate"
}

update_resp = requests.put(
    f"{BASE_URL}/api/user/profile",
    json=update_data,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
)

print(f"Update Status: {update_resp.status_code}")

if update_resp.status_code == 200:
    data = update_resp.json()
    print("SUCCESS! Profile updated")
    print(f"Age: {data['profile'].get('age')}")
    print(f"Weight: {data['profile'].get('weight')}")
    print(f"Height: {data['profile'].get('height')}")
    print(f"Gender: {data['profile'].get('gender')}")
    print(f"Training Level: {data['profile'].get('training_level')}")
else:
    print(f"Error: {update_resp.text}")

# Verify by getting profile
print("\n=== VERIFYING PROFILE ===")
get_resp = requests.get(
    f"{BASE_URL}/api/user/profile",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Get Status: {get_resp.status_code}")

if get_resp.status_code == 200:
    profile = get_resp.json()
    print("Profile retrieved successfully")
    print(f"Age: {profile.get('age')}")
    print(f"Weight: {profile.get('weight')}")
    print(f"Height: {profile.get('height')}")
    print(f"Gender: {profile.get('gender')}")
    print(f"Training Level: {profile.get('training_level')}")
else:
    print(f"Error: {get_resp.text}")

print("\n=== TEST COMPLETE ===")

